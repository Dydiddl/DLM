# SQLite Basic Guide and Usage Manual

## 목차
1. [SQLite란?](#sqlite란)
2. [SQLite의 장점](#sqlite의-장점)
3. [파이썬에서 SQLite 사용하기](#파이썬에서-sqlite-사용하기)
4. [기본 SQL 명령어](#기본-sql-명령어)
5. [파이썬 SQLite API](#파이썬-sqlite-api)
6. [실제 사용 예시](#실제-사용-예시)
7. [모범 사례](#모범-사례)

## SQLite란?

SQLite는 **서버가 필요 없는 경량 데이터베이스**입니다. 
- 단일 파일로 모든 데이터를 저장
- 파이썬에 내장되어 있어 별도 설치 불필요
- ACID 트랜잭션 지원
- 대부분의 SQL 표준 지원

## SQLite의 장점

### 1. 간단함
- 서버 설정 불필요
- 단일 파일로 관리
- 복잡한 설치 과정 없음

### 2. 성능
- 빠른 읽기/쓰기 속도
- 메모리 효율적
- 동시 접근 제한적이지만 충분히 빠름

### 3. 호환성
- 파이썬 내장
- 크로스 플랫폼 지원
- 다양한 프로그래밍 언어 지원

### 4. 안정성
- ACID 트랜잭션 지원
- 데이터 무결성 보장
- 충돌 복구 기능

## 파이썬에서 SQLite 사용하기

### 기본 연결
```python
import sqlite3

# 데이터베이스 연결
conn = sqlite3.connect('workers.db')
cursor = conn.cursor()

# 작업 완료 후 연결 종료
conn.close()
```

### 컨텍스트 매니저 사용 (권장)
```python
import sqlite3

with sqlite3.connect('workers.db') as conn:
    cursor = conn.cursor()
    # 데이터베이스 작업 수행
    # 자동으로 연결 종료
```

## 기본 SQL 명령어

### 테이블 생성 (CREATE TABLE)
```sql
CREATE TABLE workers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    id_number TEXT UNIQUE NOT NULL,
    phone TEXT,
    team TEXT,
    bank_account TEXT,
    safety_training BOOLEAN DEFAULT FALSE,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 데이터 삽입 (INSERT)
```sql
INSERT INTO workers (name, id_number, phone, team) 
VALUES ('홍길동', '123456-1234567', '010-1234-5678', '건설팀');
```

### 데이터 조회 (SELECT)
```sql
-- 모든 근로자 조회
SELECT * FROM workers;

-- 특정 조건으로 조회
SELECT name, phone FROM workers WHERE team = '건설팀';

-- 정렬
SELECT * FROM workers ORDER BY name ASC;

-- 제한
SELECT * FROM workers LIMIT 10;
```

### 데이터 수정 (UPDATE)
```sql
UPDATE workers 
SET phone = '010-9876-5432', updated_at = CURRENT_TIMESTAMP 
WHERE id = 1;
```

### 데이터 삭제 (DELETE)
```sql
DELETE FROM workers WHERE id = 1;
```

## 파이썬 SQLite API

### 기본 사용법
```python
import sqlite3
from typing import List, Dict, Optional

class WorkerDatabase:
    def __init__(self, db_path: str = "workers.db"):
        self.db_path = db_path
    
    def execute_query(self, query: str, params: tuple = ()) -> List[tuple]:
        """쿼리 실행"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.fetchall()
    
    def execute_update(self, query: str, params: tuple = ()) -> int:
        """데이터 수정 쿼리 실행"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            return cursor.rowcount
```

### 파라미터화된 쿼리 (SQL 인젝션 방지)
```python
# 좋은 예 (파라미터화)
cursor.execute("SELECT * FROM workers WHERE name = ?", (name,))

# 나쁜 예 (SQL 인젝션 위험)
cursor.execute(f"SELECT * FROM workers WHERE name = '{name}'")
```

### 딕셔너리 형태로 결과 받기
```python
def get_workers_as_dict(self) -> List[Dict]:
    """근로자 목록을 딕셔너리 형태로 반환"""
    with sqlite3.connect(self.db_path) as conn:
        conn.row_factory = sqlite3.Row  # 딕셔너리 형태로 반환
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM workers")
        return [dict(row) for row in cursor.fetchall()]
```

## 실제 사용 예시

### 1. 근로자 추가
```python
def add_worker(self, name: str, id_number: str, phone: str = None, team: str = None) -> bool:
    """근로자 추가"""
    try:
        query = """
            INSERT INTO workers (name, id_number, phone, team)
            VALUES (?, ?, ?, ?)
        """
        self.execute_update(query, (name, id_number, phone, team))
        return True
    except sqlite3.IntegrityError:
        print("이미 존재하는 주민등록번호입니다.")
        return False
```

### 2. 근로자 검색
```python
def search_workers(self, name: Optional[str] = None, team: Optional[str] = None) -> List[Dict]:
    """근로자 검색"""
    query = "SELECT * FROM workers WHERE 1=1"
    params = []
    
    if name:
        query += " AND name LIKE ?"
        params.append(f"%{name}%")
    
    if team:
        query += " AND team = ?"
        params.append(team)
    
    with sqlite3.connect(self.db_path) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]
```

### 3. 근로자 정보 수정
```python
def update_worker(self, worker_id: int, **kwargs) -> bool:
    """근로자 정보 수정"""
    if not kwargs:
        return False
    
    set_clause = ", ".join([f"{key} = ?" for key in kwargs.keys()])
    query = f"UPDATE workers SET {set_clause}, updated_at = CURRENT_TIMESTAMP WHERE id = ?"
    
    params = list(kwargs.values()) + [worker_id]
    return self.execute_update(query, tuple(params)) > 0
```

### 4. 통계 조회
```python
def get_statistics(self) -> Dict:
    """근로자 통계 조회"""
    queries = {
        'total_workers': "SELECT COUNT(*) FROM workers",
        'teams': "SELECT team, COUNT(*) as count FROM workers GROUP BY team",
        'safety_training': "SELECT COUNT(*) FROM workers WHERE safety_training = 1"
    }
    
    stats = {}
    for key, query in queries.items():
        result = self.execute_query(query)
        stats[key] = result[0][0] if key != 'teams' else result
    
    return stats
```

## 모범 사례

### 1. 연결 관리
```python
# 항상 컨텍스트 매니저 사용
with sqlite3.connect('workers.db') as conn:
    cursor = conn.cursor()
    # 작업 수행
```

### 2. 트랜잭션 사용
```python
def batch_add_workers(self, workers: List[Dict]) -> bool:
    """여러 근로자 일괄 추가"""
    try:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            for worker in workers:
                cursor.execute("""
                    INSERT INTO workers (name, id_number, phone, team)
                    VALUES (?, ?, ?, ?)
                """, (worker['name'], worker['id_number'], worker['phone'], worker['team']))
            conn.commit()
            return True
    except Exception as e:
        print(f"일괄 추가 중 오류: {e}")
        return False
```

### 3. 인덱스 생성
```sql
-- 자주 검색하는 컬럼에 인덱스 생성
CREATE INDEX idx_workers_name ON workers(name);
CREATE INDEX idx_workers_team ON workers(team);
CREATE INDEX idx_workers_id_number ON workers(id_number);
```

### 4. 백업 및 복원
```python
import shutil
from datetime import datetime

def backup_database(self, backup_path: str = None) -> str:
    """데이터베이스 백업"""
    if not backup_path:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = f"backup_workers_{timestamp}.db"
    
    shutil.copy2(self.db_path, backup_path)
    return backup_path
```

### 5. 데이터 검증
```python
def validate_worker_data(self, worker_data: Dict) -> bool:
    """근로자 데이터 검증"""
    required_fields = ['name', 'id_number']
    
    for field in required_fields:
        if field not in worker_data or not worker_data[field]:
            print(f"필수 필드가 누락되었습니다: {field}")
            return False
    
    # 주민등록번호 형식 검증
    if not self.validate_id_number(worker_data['id_number']):
        print("잘못된 주민등록번호 형식입니다.")
        return False
    
    return True
```

## 주의사항

1. **동시 접근**: SQLite는 동시 쓰기 작업에 제한이 있음
2. **파일 크기**: 대용량 데이터의 경우 성능 저하 가능
3. **백업**: 정기적인 백업 필요
4. **인덱스**: 자주 검색하는 컬럼에 인덱스 생성 권장

## 다음 단계

- [고급 SQLite 사용법](./advanced_usage.md)
- [성능 최적화](./performance_optimization.md)
- [마이그레이션 가이드](./migration_guide.md)
- [문제 해결](./troubleshooting.md) 