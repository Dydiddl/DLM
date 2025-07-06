# Excel to SQLite Migration Guide

## 목차
1. [마이그레이션 준비](#마이그레이션-준비)
2. [데이터 분석](#데이터-분석)
3. [스키마 설계](#스키마-설계)
4. [마이그레이션 스크립트](#마이그레이션-스크립트)
5. [데이터 검증](#데이터-검증)
6. [테스트](#테스트)
7. [문제 해결](#문제-해결)

## 마이그레이션 준비

### 현재 상황 분석
- **현재**: 엑셀 파일에서 Lookup 함수 사용
- **목표**: SQLite 데이터베이스로 전환
- **장점**: 
  - 빠른 검색 및 필터링
  - 데이터 무결성 보장
  - 프로그래밍 언어 연동
  - 백업 및 복원 용이

### 필요한 도구
```python
# 필수 라이브러리
import pandas as pd
import sqlite3
import numpy as np
from typing import Dict, List, Optional
import logging
```

## 데이터 분석

### 엑셀 파일 구조 분석
```python
def analyze_excel_structure(excel_path: str, sheet_name: str = "Sheet1") -> Dict:
    """엑셀 파일 구조 분석"""
    try:
        df = pd.read_excel(excel_path, sheet_name=sheet_name)
        
        analysis = {
            'total_rows': len(df),
            'total_columns': len(df.columns),
            'columns': list(df.columns),
            'data_types': df.dtypes.to_dict(),
            'null_counts': df.isnull().sum().to_dict(),
            'duplicate_rows': df.duplicated().sum(),
            'sample_data': df.head(5).to_dict('records')
        }
        
        return analysis
    except Exception as e:
        print(f"엑셀 파일 분석 중 오류: {e}")
        return {}

# 사용 예시
analysis = analyze_excel_structure("workers.xlsx")
print("엑셀 파일 분석 결과:")
for key, value in analysis.items():
    print(f"{key}: {value}")
```

### 데이터 품질 검사
```python
def check_data_quality(df: pd.DataFrame) -> Dict:
    """데이터 품질 검사"""
    quality_report = {
        'missing_data': {},
        'duplicate_records': 0,
        'format_issues': {},
        'data_consistency': {}
    }
    
    # 누락 데이터 확인
    for column in df.columns:
        missing_count = df[column].isnull().sum()
        if missing_count > 0:
            quality_report['missing_data'][column] = missing_count
    
    # 중복 레코드 확인
    quality_report['duplicate_records'] = df.duplicated().sum()
    
    # 주민등록번호 형식 검사
    if '주민등록번호' in df.columns:
        invalid_ids = df[~df['주민등록번호'].str.match(r'^\d{6}-\d{7}$', na=False)]
        quality_report['format_issues']['주민등록번호'] = len(invalid_ids)
    
    # 휴대전화번호 형식 검사
    if '휴대전화번호' in df.columns:
        invalid_phones = df[~df['휴대전화번호'].str.match(r'^01[0-9]-\d{3,4}-\d{4}$', na=False)]
        quality_report['format_issues']['휴대전화번호'] = len(invalid_phones)
    
    return quality_report
```

## 스키마 설계

### 기본 테이블 구조
```sql
-- 팀 테이블
CREATE TABLE teams (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 근로자 테이블
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

-- 문서 테이블
CREATE TABLE documents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    worker_id INTEGER NOT NULL,
    document_type TEXT NOT NULL CHECK (document_type IN ('id_card', 'bank_book')),
    file_path TEXT NOT NULL,
    file_name TEXT NOT NULL,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (worker_id) REFERENCES workers(id) ON DELETE CASCADE
);

-- 감사 로그 테이블
CREATE TABLE audit_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    operation TEXT NOT NULL,
    table_name TEXT NOT NULL,
    record_id INTEGER,
    old_values TEXT,
    new_values TEXT,
    user TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 인덱스 생성
```sql
-- 성능 최적화를 위한 인덱스
CREATE INDEX idx_workers_name ON workers(name);
CREATE INDEX idx_workers_id_number ON workers(id_number);
CREATE INDEX idx_workers_team_id ON workers(team_id);
CREATE INDEX idx_workers_safety_training ON workers(safety_training);
CREATE INDEX idx_workers_created_at ON workers(created_at);
CREATE INDEX idx_documents_worker_id ON documents(worker_id);
CREATE INDEX idx_documents_type ON documents(document_type);
```

## 마이그레이션 스크립트

### 기본 마이그레이션 클래스
```python
class ExcelToSQLiteMigrator:
    def __init__(self, excel_path: str, db_path: str = "workers.db"):
        self.excel_path = excel_path
        self.db_path = db_path
        self.setup_logging()
    
    def setup_logging(self):
        """로깅 설정"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('migration.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def create_database_schema(self):
        """데이터베이스 스키마 생성"""
        schema_queries = [
            # 팀 테이블
            """CREATE TABLE IF NOT EXISTS teams (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )""",
            
            # 근로자 테이블
            """CREATE TABLE IF NOT EXISTS workers (
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
            )""",
            
            # 문서 테이블
            """CREATE TABLE IF NOT EXISTS documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                worker_id INTEGER NOT NULL,
                document_type TEXT NOT NULL CHECK (document_type IN ('id_card', 'bank_book')),
                file_path TEXT NOT NULL,
                file_name TEXT NOT NULL,
                uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (worker_id) REFERENCES workers(id) ON DELETE CASCADE
            )""",
            
            # 감사 로그 테이블
            """CREATE TABLE IF NOT EXISTS audit_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                operation TEXT NOT NULL,
                table_name TEXT NOT NULL,
                record_id INTEGER,
                old_values TEXT,
                new_values TEXT,
                user TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )"""
        ]
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            for query in schema_queries:
                cursor.execute(query)
            conn.commit()
        
        self.logger.info("데이터베이스 스키마 생성 완료")
    
    def create_indexes(self):
        """인덱스 생성"""
        index_queries = [
            "CREATE INDEX IF NOT EXISTS idx_workers_name ON workers(name)",
            "CREATE INDEX IF NOT EXISTS idx_workers_id_number ON workers(id_number)",
            "CREATE INDEX IF NOT EXISTS idx_workers_team_id ON workers(team_id)",
            "CREATE INDEX IF NOT EXISTS idx_workers_safety_training ON workers(safety_training)",
            "CREATE INDEX IF NOT EXISTS idx_workers_created_at ON workers(created_at)",
            "CREATE INDEX IF NOT EXISTS idx_documents_worker_id ON documents(worker_id)",
            "CREATE INDEX IF NOT EXISTS idx_documents_type ON documents(document_type)"
        ]
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            for query in index_queries:
                cursor.execute(query)
            conn.commit()
        
        self.logger.info("인덱스 생성 완료")
```

### 데이터 변환 및 마이그레이션
```python
def migrate_teams(self, df: pd.DataFrame) -> Dict[str, int]:
    """팀 데이터 마이그레이션"""
    team_mapping = {}
    
    # 고유한 팀 목록 추출
    unique_teams = df['소속팀'].dropna().unique()
    
    with sqlite3.connect(self.db_path) as conn:
        cursor = conn.cursor()
        
        for team_name in unique_teams:
            if team_name and team_name.strip():
                try:
                    cursor.execute(
                        "INSERT INTO teams (name) VALUES (?)",
                        (team_name.strip(),)
                    )
                    team_id = cursor.lastrowid
                    team_mapping[team_name] = team_id
                    self.logger.info(f"팀 추가: {team_name} (ID: {team_id})")
                except sqlite3.IntegrityError:
                    # 이미 존재하는 팀인 경우 ID 조회
                    cursor.execute("SELECT id FROM teams WHERE name = ?", (team_name.strip(),))
                    team_id = cursor.fetchone()[0]
                    team_mapping[team_name] = team_id
        
        conn.commit()
    
    return team_mapping

def migrate_workers(self, df: pd.DataFrame, team_mapping: Dict[str, int]):
    """근로자 데이터 마이그레이션"""
    success_count = 0
    error_count = 0
    
    with sqlite3.connect(self.db_path) as conn:
        cursor = conn.cursor()
        
        for index, row in df.iterrows():
            try:
                # 데이터 정제
                name = str(row['이름']).strip() if pd.notna(row['이름']) else None
                id_number = str(row['주민등록번호']).strip() if pd.notna(row['주민등록번호']) else None
                phone = str(row['휴대전화번호']).strip() if pd.notna(row['휴대전화번호']) else None
                team_name = str(row['소속팀']).strip() if pd.notna(row['소속팀']) else None
                bank_account = str(row['계좌번호']).strip() if pd.notna(row['계좌번호']) else None
                safety_training = bool(row['안전교육']) if pd.notna(row['안전교육']) else False
                notes = str(row['비고']).strip() if pd.notna(row['비고']) else None
                
                # 필수 필드 검증
                if not name or not id_number:
                    self.logger.warning(f"필수 필드 누락: 행 {index + 2}")
                    error_count += 1
                    continue
                
                # 팀 ID 매핑
                team_id = team_mapping.get(team_name) if team_name else None
                
                # 근로자 데이터 삽입
                cursor.execute("""
                    INSERT INTO workers (name, id_number, phone, team_id, bank_account, safety_training, notes)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (name, id_number, phone, team_id, bank_account, safety_training, notes))
                
                success_count += 1
                
                if success_count % 100 == 0:
                    self.logger.info(f"진행 상황: {success_count}명 처리 완료")
                
            except sqlite3.IntegrityError as e:
                self.logger.error(f"중복 데이터 또는 제약 조건 위반: 행 {index + 2}, 오류: {e}")
                error_count += 1
            except Exception as e:
                self.logger.error(f"데이터 삽입 오류: 행 {index + 2}, 오류: {e}")
                error_count += 1
        
        conn.commit()
    
    self.logger.info(f"근로자 마이그레이션 완료: 성공 {success_count}명, 실패 {error_count}명")
    return success_count, error_count

def run_migration(self, sheet_name: str = "Sheet1"):
    """전체 마이그레이션 실행"""
    try:
        self.logger.info("마이그레이션 시작")
        
        # 1. 엑셀 파일 읽기
        self.logger.info("엑셀 파일 읽기 중...")
        df = pd.read_excel(self.excel_path, sheet_name=sheet_name)
        self.logger.info(f"총 {len(df)}행의 데이터 읽기 완료")
        
        # 2. 데이터 품질 검사
        self.logger.info("데이터 품질 검사 중...")
        quality_report = check_data_quality(df)
        self.logger.info(f"품질 검사 결과: {quality_report}")
        
        # 3. 데이터베이스 스키마 생성
        self.logger.info("데이터베이스 스키마 생성 중...")
        self.create_database_schema()
        
        # 4. 팀 데이터 마이그레이션
        self.logger.info("팀 데이터 마이그레이션 중...")
        team_mapping = self.migrate_teams(df)
        
        # 5. 근로자 데이터 마이그레이션
        self.logger.info("근로자 데이터 마이그레이션 중...")
        success_count, error_count = self.migrate_workers(df, team_mapping)
        
        # 6. 인덱스 생성
        self.logger.info("인덱스 생성 중...")
        self.create_indexes()
        
        # 7. 마이그레이션 완료 보고
        self.logger.info("마이그레이션 완료!")
        self.generate_migration_report(success_count, error_count, quality_report)
        
    except Exception as e:
        self.logger.error(f"마이그레이션 중 오류 발생: {e}")
        raise
```

## 데이터 검증

### 마이그레이션 결과 검증
```python
def verify_migration(self) -> Dict:
    """마이그레이션 결과 검증"""
    verification_results = {}
    
    with sqlite3.connect(self.db_path) as conn:
        cursor = conn.cursor()
        
        # 1. 총 레코드 수 확인
        cursor.execute("SELECT COUNT(*) FROM workers")
        worker_count = cursor.fetchone()[0]
        verification_results['total_workers'] = worker_count
        
        cursor.execute("SELECT COUNT(*) FROM teams")
        team_count = cursor.fetchone()[0]
        verification_results['total_teams'] = team_count
        
        # 2. 팀별 근로자 수 확인
        cursor.execute("""
            SELECT t.name, COUNT(w.id) as worker_count
            FROM teams t
            LEFT JOIN workers w ON t.id = w.team_id
            GROUP BY t.id, t.name
            ORDER BY worker_count DESC
        """)
        team_stats = cursor.fetchall()
        verification_results['team_statistics'] = team_stats
        
        # 3. 안전교육 이수자 수 확인
        cursor.execute("SELECT COUNT(*) FROM workers WHERE safety_training = 1")
        trained_count = cursor.fetchone()[0]
        verification_results['safety_trained_count'] = trained_count
        
        # 4. 중복 주민등록번호 확인
        cursor.execute("""
            SELECT id_number, COUNT(*) as count
            FROM workers
            GROUP BY id_number
            HAVING count > 1
        """)
        duplicates = cursor.fetchall()
        verification_results['duplicate_id_numbers'] = duplicates
        
        # 5. 데이터 무결성 확인
        cursor.execute("""
            SELECT COUNT(*) FROM workers w
            LEFT JOIN teams t ON w.team_id = t.id
            WHERE w.team_id IS NOT NULL AND t.id IS NULL
        """)
        orphaned_workers = cursor.fetchone()[0]
        verification_results['orphaned_workers'] = orphaned_workers
    
    return verification_results

def generate_migration_report(self, success_count: int, error_count: int, quality_report: Dict):
    """마이그레이션 보고서 생성"""
    verification_results = self.verify_migration()
    
    report = f"""
=== 마이그레이션 완료 보고서 ===

📊 마이그레이션 결과:
- 성공: {success_count}명
- 실패: {error_count}명
- 성공률: {success_count/(success_count+error_count)*100:.1f}%

📈 데이터베이스 현황:
- 총 근로자: {verification_results['total_workers']}명
- 총 팀: {verification_results['total_teams']}개
- 안전교육 이수자: {verification_results['safety_trained_count']}명

⚠️ 주의사항:
- 중복 주민등록번호: {len(verification_results['duplicate_id_numbers'])}건
- 고아 레코드: {verification_results['orphaned_workers']}건

📋 품질 검사 결과:
{quality_report}
"""
    
    # 보고서 파일 저장
    with open('migration_report.txt', 'w', encoding='utf-8') as f:
        f.write(report)
    
    self.logger.info("마이그레이션 보고서 생성 완료: migration_report.txt")
    print(report)
```

## 테스트

### 마이그레이션 테스트
```python
def test_migration(self):
    """마이그레이션 테스트"""
    # 1. 샘플 데이터로 테스트
    test_data = pd.DataFrame({
        '이름': ['홍길동', '김철수', '이영희'],
        '주민등록번호': ['123456-1234567', '234567-2345678', '345678-3456789'],
        '휴대전화번호': ['010-1234-5678', '010-2345-6789', '010-3456-7890'],
        '소속팀': ['건설팀', '건설팀', '전기팀'],
        '계좌번호': ['123-456-789', '234-567-890', '345-678-901'],
        '안전교육': [True, False, True],
        '비고': ['테스트1', '테스트2', '테스트3']
    })
    
    # 테스트용 데이터베이스 생성
    test_db_path = "test_workers.db"
    test_migrator = ExcelToSQLiteMigrator("test.xlsx", test_db_path)
    
    # 테스트 실행
    test_migrator.create_database_schema()
    team_mapping = test_migrator.migrate_teams(test_data)
    success_count, error_count = test_migrator.migrate_workers(test_data, team_mapping)
    
    # 결과 검증
    verification_results = test_migrator.verify_migration()
    
    print("테스트 결과:")
    print(f"성공: {success_count}, 실패: {error_count}")
    print(f"검증 결과: {verification_results}")
    
    # 테스트 데이터베이스 정리
    import os
    if os.path.exists(test_db_path):
        os.remove(test_db_path)
```

## 문제 해결

### 일반적인 문제와 해결책

#### 1. 인코딩 문제
```python
def handle_encoding_issues(self, excel_path: str) -> pd.DataFrame:
    """인코딩 문제 해결"""
    try:
        # UTF-8로 시도
        return pd.read_excel(excel_path, encoding='utf-8')
    except UnicodeDecodeError:
        try:
            # CP949로 시도
            return pd.read_excel(excel_path, encoding='cp949')
        except UnicodeDecodeError:
            # 기본 인코딩으로 시도
            return pd.read_excel(excel_path)
```

#### 2. 데이터 타입 변환 문제
```python
def clean_data_types(self, df: pd.DataFrame) -> pd.DataFrame:
    """데이터 타입 정제"""
    # 날짜 컬럼 처리
    date_columns = ['등록일', '수정일']
    for col in date_columns:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors='coerce')
    
    # 숫자 컬럼 처리
    numeric_columns = ['급여', '근무시간']
    for col in numeric_columns:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # 불린 컬럼 처리
    boolean_columns = ['안전교육', '활성상태']
    for col in boolean_columns:
        if col in df.columns:
            df[col] = df[col].map({'Y': True, 'N': False, '예': True, '아니오': False})
            df[col] = df[col].fillna(False)
    
    return df
```

#### 3. 중복 데이터 처리
```python
def handle_duplicates(self, df: pd.DataFrame) -> pd.DataFrame:
    """중복 데이터 처리"""
    # 주민등록번호 기준 중복 제거 (최신 데이터 유지)
    df = df.sort_values('등록일', ascending=False)
    df = df.drop_duplicates(subset=['주민등록번호'], keep='first')
    
    return df
```

### 롤백 방법
```python
def rollback_migration(self):
    """마이그레이션 롤백"""
    try:
        # 데이터베이스 파일 백업
        import shutil
        from datetime import datetime
        
        backup_name = f"rollback_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
        shutil.copy2(self.db_path, backup_name)
        
        # 데이터베이스 파일 삭제
        import os
        os.remove(self.db_path)
        
        self.logger.info(f"롤백 완료. 백업 파일: {backup_name}")
        return True
        
    except Exception as e:
        self.logger.error(f"롤백 중 오류: {e}")
        return False
```

이 가이드를 따라하면 엑셀 데이터를 안전하고 효율적으로 SQLite로 마이그레이션할 수 있습니다. 