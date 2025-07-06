# SQLite Advanced Usage and Optimization

## 목차
1. [트랜잭션 관리](#트랜잭션-관리)
2. [인덱스 최적화](#인덱스-최적화)
3. [외래 키와 관계](#외래-키와-관계)
4. [뷰와 트리거](#뷰와-트리거)
5. [백업과 복원](#백업과-복원)
6. [성능 모니터링](#성능-모니터링)
7. [보안 고려사항](#보안-고려사항)

## 트랜잭션 관리

### 기본 트랜잭션
```python
import sqlite3
from contextlib import contextmanager

class WorkerDatabase:
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
    
    def batch_operations(self, operations: List[tuple]) -> bool:
        """일괄 작업 수행"""
        try:
            with self.transaction() as conn:
                cursor = conn.cursor()
                for query, params in operations:
                    cursor.execute(query, params)
            return True
        except Exception as e:
            print(f"일괄 작업 중 오류: {e}")
            return False
```

### 트랜잭션 격리 수준
```python
def set_isolation_level(self, level: str = "IMMEDIATE"):
    """트랜잭션 격리 수준 설정"""
    with sqlite3.connect(self.db_path) as conn:
        conn.isolation_level = level  # DEFERRED, IMMEDIATE, EXCLUSIVE
```

## 인덱스 최적화

### 인덱스 생성
```sql
-- 단일 컬럼 인덱스
CREATE INDEX idx_workers_name ON workers(name);

-- 복합 인덱스
CREATE INDEX idx_workers_team_name ON workers(team, name);

-- 유니크 인덱스
CREATE UNIQUE INDEX idx_workers_id_number ON workers(id_number);

-- 부분 인덱스 (조건부)
CREATE INDEX idx_active_workers ON workers(name) WHERE safety_training = 1;
```

### 인덱스 관리
```python
def create_indexes(self):
    """성능 최적화를 위한 인덱스 생성"""
    indexes = [
        "CREATE INDEX IF NOT EXISTS idx_workers_name ON workers(name)",
        "CREATE INDEX IF NOT EXISTS idx_workers_team ON workers(team)",
        "CREATE INDEX IF NOT EXISTS idx_workers_safety ON workers(safety_training)",
        "CREATE INDEX IF NOT EXISTS idx_workers_created ON workers(created_at)"
    ]
    
    with sqlite3.connect(self.db_path) as conn:
        cursor = conn.cursor()
        for index_query in indexes:
            cursor.execute(index_query)
        conn.commit()

def analyze_indexes(self):
    """인덱스 사용 현황 분석"""
    query = """
        SELECT name, sql FROM sqlite_master 
        WHERE type = 'index' AND name NOT LIKE 'sqlite_%'
    """
    return self.execute_query(query)
```

## 외래 키와 관계

### 관계형 스키마 설계
```sql
-- 팀 테이블
CREATE TABLE teams (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 근로자 테이블 (팀 참조)
CREATE TABLE workers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    id_number TEXT UNIQUE NOT NULL,
    phone TEXT,
    team_id INTEGER,
    bank_account TEXT,
    safety_training BOOLEAN DEFAULT FALSE,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (team_id) REFERENCES teams(id) ON DELETE SET NULL
);

-- 문서 테이블 (근로자 참조)
CREATE TABLE documents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    worker_id INTEGER NOT NULL,
    document_type TEXT NOT NULL CHECK (document_type IN ('id_card', 'bank_book')),
    file_path TEXT NOT NULL,
    file_name TEXT NOT NULL,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (worker_id) REFERENCES workers(id) ON DELETE CASCADE
);
```

### 조인 쿼리
```python
def get_workers_with_teams(self) -> List[Dict]:
    """팀 정보와 함께 근로자 조회"""
    query = """
        SELECT w.*, t.name as team_name, t.description as team_description
        FROM workers w
        LEFT JOIN teams t ON w.team_id = t.id
        ORDER BY w.name
    """
    
    with sqlite3.connect(self.db_path) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(query)
        return [dict(row) for row in cursor.fetchall()]

def get_worker_with_documents(self, worker_id: int) -> Dict:
    """문서와 함께 근로자 정보 조회"""
    query = """
        SELECT w.*, t.name as team_name,
               d.document_type, d.file_name, d.uploaded_at
        FROM workers w
        LEFT JOIN teams t ON w.team_id = t.id
        LEFT JOIN documents d ON w.id = d.worker_id
        WHERE w.id = ?
    """
    
    with sqlite3.connect(self.db_path) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(query, (worker_id,))
        rows = cursor.fetchall()
        
        if not rows:
            return None
        
        worker = dict(rows[0])
        worker['documents'] = []
        
        for row in rows:
            if row['document_type']:
                worker['documents'].append({
                    'type': row['document_type'],
                    'file_name': row['file_name'],
                    'uploaded_at': row['uploaded_at']
                })
        
        return worker
```

## 뷰와 트리거

### 뷰 생성
```sql
-- 팀별 근로자 통계 뷰
CREATE VIEW team_statistics AS
SELECT 
    t.name as team_name,
    COUNT(w.id) as worker_count,
    SUM(CASE WHEN w.safety_training = 1 THEN 1 ELSE 0 END) as trained_count,
    AVG(CASE WHEN w.safety_training = 1 THEN 1.0 ELSE 0.0 END) as training_rate
FROM teams t
LEFT JOIN workers w ON t.id = w.team_id
GROUP BY t.id, t.name;

-- 최근 등록된 근로자 뷰
CREATE VIEW recent_workers AS
SELECT name, id_number, team_id, created_at
FROM workers
WHERE created_at >= date('now', '-30 days')
ORDER BY created_at DESC;
```

### 트리거 생성
```sql
-- 업데이트 시간 자동 갱신 트리거
CREATE TRIGGER update_worker_timestamp
    AFTER UPDATE ON workers
    FOR EACH ROW
BEGIN
    UPDATE workers SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

-- 팀 삭제 시 근로자 팀 정보 초기화 트리거
CREATE TRIGGER clear_worker_team
    AFTER DELETE ON teams
    FOR EACH ROW
BEGIN
    UPDATE workers SET team_id = NULL WHERE team_id = OLD.id;
END;
```

## 백업과 복원

### 자동 백업 시스템
```python
import shutil
import os
from datetime import datetime, timedelta
from pathlib import Path

class DatabaseBackup:
    def __init__(self, db_path: str, backup_dir: str = "backups"):
        self.db_path = db_path
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(exist_ok=True)
    
    def create_backup(self, backup_name: str = None) -> str:
        """데이터베이스 백업 생성"""
        if not backup_name:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"backup_{timestamp}.db"
        
        backup_path = self.backup_dir / backup_name
        
        # WAL 모드에서 안전한 백업
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("VACUUM INTO ?", (str(backup_path),))
        
        return str(backup_path)
    
    def restore_backup(self, backup_path: str) -> bool:
        """백업에서 복원"""
        try:
            shutil.copy2(backup_path, self.db_path)
            return True
        except Exception as e:
            print(f"복원 중 오류: {e}")
            return False
    
    def cleanup_old_backups(self, days: int = 30):
        """오래된 백업 파일 정리"""
        cutoff_date = datetime.now() - timedelta(days=days)
        
        for backup_file in self.backup_dir.glob("backup_*.db"):
            if backup_file.stat().st_mtime < cutoff_date.timestamp():
                backup_file.unlink()
                print(f"삭제된 백업: {backup_file}")
```

### 온라인 백업
```python
def online_backup(self, backup_path: str) -> bool:
    """데이터베이스 사용 중에도 백업 가능"""
    try:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("VACUUM INTO ?", (backup_path,))
        return True
    except Exception as e:
        print(f"온라인 백업 중 오류: {e}")
        return False
```

## 성능 모니터링

### 쿼리 성능 분석
```python
def analyze_query_performance(self, query: str, params: tuple = ()) -> Dict:
    """쿼리 성능 분석"""
    with sqlite3.connect(self.db_path) as conn:
        cursor = conn.cursor()
        
        # 실행 계획 분석
        cursor.execute(f"EXPLAIN QUERY PLAN {query}", params)
        plan = cursor.fetchall()
        
        # 실행 시간 측정
        import time
        start_time = time.time()
        cursor.execute(query, params)
        execution_time = time.time() - start_time
        
        return {
            'execution_plan': plan,
            'execution_time': execution_time,
            'row_count': len(cursor.fetchall())
        }

def get_database_stats(self) -> Dict:
    """데이터베이스 통계 정보"""
    queries = {
        'table_sizes': """
            SELECT name, sql FROM sqlite_master 
            WHERE type = 'table' AND name NOT LIKE 'sqlite_%'
        """,
        'index_usage': """
            SELECT name, sql FROM sqlite_master 
            WHERE type = 'index' AND name NOT LIKE 'sqlite_%'
        """,
        'database_size': "PRAGMA page_count * PRAGMA page_size"
    }
    
    stats = {}
    with sqlite3.connect(self.db_path) as conn:
        cursor = conn.cursor()
        
        for key, query in queries.items():
            cursor.execute(query)
            stats[key] = cursor.fetchall()
    
    return stats
```

## 보안 고려사항

### 입력 검증
```python
import re
from typing import Optional

class SecurityValidator:
    @staticmethod
    def sanitize_sql_input(input_str: str) -> str:
        """SQL 인젝션 방지를 위한 입력 정제"""
        # 위험한 문자 제거
        dangerous_chars = ["'", '"', ';', '--', '/*', '*/']
        for char in dangerous_chars:
            input_str = input_str.replace(char, '')
        return input_str.strip()
    
    @staticmethod
    def validate_id_number(id_number: str) -> bool:
        """주민등록번호 형식 검증"""
        pattern = r'^\d{6}-\d{7}$'
        if not re.match(pattern, id_number):
            return False
        
        # 체크섬 검증
        digits = id_number.replace('-', '')
        weights = [2, 3, 4, 5, 6, 7, 2, 3, 4, 5, 6, 7]
        
        checksum = sum(int(d) * w for d, w in zip(digits[:-1], weights))
        check_digit = (11 - (checksum % 11)) % 10
        
        return int(digits[-1]) == check_digit
```

### 접근 제어
```python
class DatabaseAccessControl:
    def __init__(self, db_path: str):
        self.db_path = db_path
    
    def set_user_permissions(self, username: str, permissions: List[str]):
        """사용자 권한 설정"""
        # SQLite는 기본적으로 파일 기반 접근 제어
        # 추가적인 애플리케이션 레벨 권한 관리 필요
        pass
    
    def audit_log(self, operation: str, user: str, details: str):
        """감사 로그 기록"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO audit_log (operation, user, details, timestamp)
                VALUES (?, ?, ?, CURRENT_TIMESTAMP)
            """, (operation, user, details))
            conn.commit()
```

### 암호화
```python
import hashlib
import os

class DataEncryption:
    def __init__(self, encryption_key: str = None):
        self.encryption_key = encryption_key or os.getenv('ENCRYPTION_KEY')
    
    def encrypt_sensitive_data(self, data: str) -> str:
        """민감 데이터 암호화"""
        if not self.encryption_key:
            return data
        
        # 간단한 해시 암호화 (실제로는 더 강력한 암호화 사용)
        return hashlib.sha256((data + self.encryption_key).encode()).hexdigest()
    
    def store_encrypted_worker_data(self, worker_data: Dict) -> bool:
        """암호화된 근로자 데이터 저장"""
        encrypted_data = {
            'name': worker_data['name'],
            'id_number': self.encrypt_sensitive_data(worker_data['id_number']),
            'phone': self.encrypt_sensitive_data(worker_data.get('phone', '')),
            'bank_account': self.encrypt_sensitive_data(worker_data.get('bank_account', ''))
        }
        
        # 암호화된 데이터 저장
        return self.save_worker_data(encrypted_data)
```

## 고급 쿼리 기법

### 윈도우 함수
```sql
-- 팀별 근로자 순위
SELECT 
    name,
    team,
    ROW_NUMBER() OVER (PARTITION BY team ORDER BY created_at) as team_rank,
    RANK() OVER (ORDER BY created_at) as overall_rank
FROM workers;

-- 팀별 누적 통계
SELECT 
    team,
    COUNT(*) OVER (PARTITION BY team) as team_count,
    COUNT(*) OVER (ORDER BY created_at) as cumulative_count
FROM workers;
```

### 재귀 쿼리 (CTE)
```sql
-- 계층적 팀 구조 (예시)
WITH RECURSIVE team_hierarchy AS (
    SELECT id, name, parent_id, 1 as level
    FROM teams
    WHERE parent_id IS NULL
    
    UNION ALL
    
    SELECT t.id, t.name, t.parent_id, th.level + 1
    FROM teams t
    JOIN team_hierarchy th ON t.parent_id = th.id
)
SELECT * FROM team_hierarchy;
```

이러한 고급 기법들을 활용하면 SQLite를 더욱 효율적으로 사용할 수 있습니다. 