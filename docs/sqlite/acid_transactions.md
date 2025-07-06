# ACID Transactions in SQLite

## 목차
1. [ACID란?](#acid란)
2. [SQLite에서의 ACID 구현](#sqlite에서의-acid-구현)
3. [트랜잭션 사용법](#트랜잭션-사용법)
4. [실제 예시](#실제-예시)
5. [성능 고려사항](#성능-고려사항)
6. [문제 해결](#문제-해결)

## ACID란?

ACID는 데이터베이스 트랜잭션이 안전하게 처리되는 것을 보장하는 4가지 속성입니다.

### 1. Atomicity (원자성)
- **정의**: 트랜잭션의 모든 작업이 **전부 성공하거나 전부 실패**해야 함
- **예시**: 근로자 정보와 문서를 함께 등록할 때, 둘 다 성공하거나 둘 다 실패해야 함

### 2. Consistency (일관성)
- **정의**: 트랜잭션 실행 전후로 데이터베이스가 **일관된 상태**를 유지해야 함
- **예시**: 주민등록번호는 고유해야 하고, 팀 ID는 실제 존재하는 팀을 참조해야 함

### 3. Isolation (격리성)
- **정의**: 동시에 실행되는 트랜잭션들이 **서로 간섭하지 않아야** 함
- **예시**: 한 사용자가 근로자 정보를 수정하는 동안 다른 사용자가 같은 정보를 읽을 수 있음

### 4. Durability (지속성)
- **정의**: 커밋된 트랜잭션은 **영구적으로 저장**되어야 함
- **예시**: 시스템 장애가 발생해도 저장된 데이터는 손실되지 않아야 함

## SQLite에서의 ACID 구현

### WAL (Write-Ahead Logging) 모드
```python
import sqlite3

def enable_wal_mode(db_path: str):
    """WAL 모드 활성화"""
    with sqlite3.connect(db_path) as conn:
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA synchronous=NORMAL")
        conn.execute("PRAGMA cache_size=10000")
        conn.execute("PRAGMA temp_store=MEMORY")
```

### 트랜잭션 격리 수준
```python
def set_isolation_level(db_path: str, level: str = "IMMEDIATE"):
    """트랜잭션 격리 수준 설정"""
    with sqlite3.connect(db_path) as conn:
        # DEFERRED: 트랜잭션 시작 시 락을 획득하지 않음
        # IMMEDIATE: 트랜잭션 시작 시 공유 락을 획득
        # EXCLUSIVE: 트랜잭션 시작 시 배타적 락을 획득
        conn.isolation_level = level
```

## 트랜잭션 사용법

### 기본 트랜잭션 패턴
```python
import sqlite3
from contextlib import contextmanager
from typing import List, Dict, Optional

class WorkerTransactionManager:
    def __init__(self, db_path: str = "workers.db"):
        self.db_path = db_path
    
    @contextmanager
    def transaction(self):
        """트랜잭션 컨텍스트 매니저"""
        conn = sqlite3.connect(self.db_path)
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()
    
    def add_worker_with_documents(self, worker_data: Dict, documents: List[Dict]) -> bool:
        """근로자와 문서를 함께 추가 (원자적 작업)"""
        try:
            with self.transaction() as conn:
                cursor = conn.cursor()
                
                # 1. 근로자 추가
                cursor.execute("""
                    INSERT INTO workers (name, id_number, phone, team_id, bank_account, safety_training, notes)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    worker_data['name'],
                    worker_data['id_number'],
                    worker_data.get('phone'),
                    worker_data.get('team_id'),
                    worker_data.get('bank_account'),
                    worker_data.get('safety_training', False),
                    worker_data.get('notes')
                ))
                
                worker_id = cursor.lastrowid
                
                # 2. 문서들 추가
                for doc in documents:
                    cursor.execute("""
                        INSERT INTO documents (worker_id, document_type, file_path, file_name)
                        VALUES (?, ?, ?, ?)
                    """, (worker_id, doc['type'], doc['path'], doc['name']))
                
                # 모든 작업이 성공하면 자동으로 커밋됨
                return True
                
        except sqlite3.IntegrityError as e:
            print(f"데이터 무결성 오류: {e}")
            return False
        except Exception as e:
            print(f"트랜잭션 오류: {e}")
            return False
```

### 복잡한 트랜잭션 예시
```python
def transfer_worker_team(self, worker_id: int, new_team_id: int, reason: str) -> bool:
    """근로자 팀 이동 (감사 로그 포함)"""
    try:
        with self.transaction() as conn:
            cursor = conn.cursor()
            
            # 1. 현재 팀 정보 조회
            cursor.execute("SELECT team_id, name FROM workers WHERE id = ?", (worker_id,))
            result = cursor.fetchone()
            if not result:
                raise ValueError("근로자를 찾을 수 없습니다")
            
            old_team_id, worker_name = result
            
            # 2. 새 팀 존재 확인
            cursor.execute("SELECT name FROM teams WHERE id = ?", (new_team_id,))
            new_team = cursor.fetchone()
            if not new_team:
                raise ValueError("새 팀을 찾을 수 없습니다")
            
            # 3. 팀 이동
            cursor.execute("""
                UPDATE workers 
                SET team_id = ?, updated_at = CURRENT_TIMESTAMP 
                WHERE id = ?
            """, (new_team_id, worker_id))
            
            # 4. 감사 로그 기록
            cursor.execute("""
                INSERT INTO audit_log (operation, table_name, record_id, old_values, new_values, user)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                'TEAM_TRANSFER',
                'workers',
                worker_id,
                f'{{"team_id": {old_team_id}}}',
                f'{{"team_id": {new_team_id}}}',
                'system'
            ))
            
            # 5. 팀 통계 업데이트 (뷰 대신 실제 테이블 사용 시)
            # cursor.execute("UPDATE team_statistics SET ...")
            
            return True
            
    except Exception as e:
        print(f"팀 이동 중 오류: {e}")
        return False
```

## 실제 예시

### 일괄 작업 (Batch Operations)
```python
def batch_update_safety_training(self, worker_ids: List[int], training_status: bool) -> Dict:
    """여러 근로자의 안전교육 상태 일괄 업데이트"""
    results = {
        'success_count': 0,
        'error_count': 0,
        'errors': []
    }
    
    try:
        with self.transaction() as conn:
            cursor = conn.cursor()
            
            for worker_id in worker_ids:
                try:
                    cursor.execute("""
                        UPDATE workers 
                        SET safety_training = ?, updated_at = CURRENT_TIMESTAMP 
                        WHERE id = ?
                    """, (training_status, worker_id))
                    
                    if cursor.rowcount > 0:
                        results['success_count'] += 1
                    else:
                        results['error_count'] += 1
                        results['errors'].append(f"근로자 ID {worker_id}를 찾을 수 없습니다")
                        
                except Exception as e:
                    results['error_count'] += 1
                    results['errors'].append(f"근로자 ID {worker_id}: {str(e)}")
            
            # 모든 작업이 성공해야 커밋됨
            return results
            
    except Exception as e:
        print(f"일괄 업데이트 중 오류: {e}")
        return results
```

### 데이터 무결성 검증
```python
def validate_worker_data_integrity(self) -> Dict:
    """근로자 데이터 무결성 검증"""
    integrity_checks = {
        'orphaned_documents': 0,
        'invalid_team_references': 0,
        'duplicate_id_numbers': 0,
        'missing_required_fields': 0
    }
    
    try:
        with self.transaction() as conn:
            cursor = conn.cursor()
            
            # 1. 고아 문서 확인 (근로자가 삭제되었지만 문서가 남은 경우)
            cursor.execute("""
                SELECT COUNT(*) FROM documents d
                LEFT JOIN workers w ON d.worker_id = w.id
                WHERE w.id IS NULL
            """)
            integrity_checks['orphaned_documents'] = cursor.fetchone()[0]
            
            # 2. 잘못된 팀 참조 확인
            cursor.execute("""
                SELECT COUNT(*) FROM workers w
                LEFT JOIN teams t ON w.team_id = t.id
                WHERE w.team_id IS NOT NULL AND t.id IS NULL
            """)
            integrity_checks['invalid_team_references'] = cursor.fetchone()[0]
            
            # 3. 중복 주민등록번호 확인
            cursor.execute("""
                SELECT id_number, COUNT(*) as count
                FROM workers
                GROUP BY id_number
                HAVING count > 1
            """)
            duplicates = cursor.fetchall()
            integrity_checks['duplicate_id_numbers'] = len(duplicates)
            
            # 4. 필수 필드 누락 확인
            cursor.execute("""
                SELECT COUNT(*) FROM workers
                WHERE name IS NULL OR name = '' OR id_number IS NULL OR id_number = ''
            """)
            integrity_checks['missing_required_fields'] = cursor.fetchone()[0]
            
            return integrity_checks
            
    except Exception as e:
        print(f"무결성 검증 중 오류: {e}")
        return integrity_checks
```

## 성능 고려사항

### 트랜잭션 크기 최적화
```python
def optimized_batch_insert(self, workers: List[Dict], batch_size: int = 100) -> bool:
    """최적화된 일괄 삽입"""
    try:
        with self.transaction() as conn:
            cursor = conn.cursor()
            
            # 배치 단위로 처리
            for i in range(0, len(workers), batch_size):
                batch = workers[i:i + batch_size]
                
                # 배치 삽입
                cursor.executemany("""
                    INSERT INTO workers (name, id_number, phone, team_id, bank_account, safety_training, notes)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, [
                    (w['name'], w['id_number'], w.get('phone'), w.get('team_id'),
                     w.get('bank_account'), w.get('safety_training', False), w.get('notes'))
                    for w in batch
                ])
                
                # 중간 커밋 (긴 트랜잭션 방지)
                conn.commit()
            
            return True
            
    except Exception as e:
        print(f"일괄 삽입 중 오류: {e}")
        return False
```

### 동시성 제어
```python
def concurrent_safe_update(self, worker_id: int, updates: Dict) -> bool:
    """동시성 안전 업데이트"""
    try:
        with self.transaction() as conn:
            cursor = conn.cursor()
            
            # 낙관적 락킹 (버전 기반)
            cursor.execute("SELECT updated_at FROM workers WHERE id = ?", (worker_id,))
            result = cursor.fetchone()
            if not result:
                return False
            
            current_version = result[0]
            
            # 업데이트 실행
            set_clause = ", ".join([f"{key} = ?" for key in updates.keys()])
            query = f"UPDATE workers SET {set_clause}, updated_at = CURRENT_TIMESTAMP WHERE id = ? AND updated_at = ?"
            
            params = list(updates.values()) + [worker_id, current_version]
            cursor.execute(query, params)
            
            if cursor.rowcount == 0:
                # 다른 트랜잭션에 의해 이미 수정됨
                return False
            
            return True
            
    except Exception as e:
        print(f"동시성 안전 업데이트 중 오류: {e}")
        return False
```

## 문제 해결

### 데드락 방지
```python
def deadlock_prevention_update(self, updates: List[tuple]) -> bool:
    """데드락 방지를 위한 순서화된 업데이트"""
    try:
        with self.transaction() as conn:
            cursor = conn.cursor()
            
            # ID 순서로 정렬하여 데드락 방지
            sorted_updates = sorted(updates, key=lambda x: x[0])
            
            for worker_id, field, value in sorted_updates:
                cursor.execute(f"UPDATE workers SET {field} = ? WHERE id = ?", (value, worker_id))
            
            return True
            
    except Exception as e:
        print(f"업데이트 중 오류: {e}")
        return False
```

### 롤백 복구
```python
def rollback_recovery(self, backup_point: str = None) -> bool:
    """롤백 복구 메커니즘"""
    try:
        if backup_point:
            # 특정 백업 지점으로 복원
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("ROLLBACK TO ?", (backup_point,))
        else:
            # 전체 롤백
            with sqlite3.connect(self.db_path) as conn:
                conn.rollback()
        
        return True
        
    except Exception as e:
        print(f"롤백 복구 중 오류: {e}")
        return False
```

### 트랜잭션 모니터링
```python
def monitor_transactions(self) -> Dict:
    """트랜잭션 상태 모니터링"""
    monitoring_data = {}
    
    try:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # 활성 트랜잭션 확인
            cursor.execute("PRAGMA lock_status")
            lock_status = cursor.fetchall()
            monitoring_data['lock_status'] = lock_status
            
            # WAL 파일 정보
            cursor.execute("PRAGMA wal_checkpoint")
            wal_info = cursor.fetchall()
            monitoring_data['wal_info'] = wal_info
            
            # 데이터베이스 크기
            cursor.execute("PRAGMA page_count")
            page_count = cursor.fetchone()[0]
            cursor.execute("PRAGMA page_size")
            page_size = cursor.fetchone()[0]
            monitoring_data['database_size'] = page_count * page_size
            
            return monitoring_data
            
    except Exception as e:
        print(f"모니터링 중 오류: {e}")
        return monitoring_data
```

## 모범 사례

### 1. 트랜잭션 크기 제한
- 한 번에 너무 많은 작업을 하지 않기
- 배치 크기를 적절히 조절하기

### 2. 적절한 격리 수준 선택
- 읽기 전용 작업: `DEFERRED`
- 일반적인 읽기/쓰기: `IMMEDIATE`
- 중요한 업데이트: `EXCLUSIVE`

### 3. 에러 처리
- 항상 예외 처리하기
- 롤백 로직 구현하기
- 사용자에게 명확한 에러 메시지 제공하기

### 4. 성능 최적화
- WAL 모드 사용하기
- 적절한 인덱스 생성하기
- 트랜잭션 크기 최적화하기

ACID 트랜잭션을 올바르게 사용하면 데이터의 일관성과 안정성을 보장할 수 있습니다. 