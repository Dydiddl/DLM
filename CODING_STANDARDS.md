# 파이썬 코드 작성 규칙 (Coding Standards)

## 목차
1. [기본 원칙](#기본-원칙)
2. [코드 스타일](#코드-스타일)
3. [네이밍 컨벤션](#네이밍-컨벤션)
4. [문서화](#문서화)
5. [에러 처리](#에러-처리)
6. [성능 최적화](#성능-최적화)
7. [보안](#보안)
8. [테스트](#테스트)

## 기본 원칙

### 1. PEP 8 준수
- 파이썬 공식 스타일 가이드인 PEP 8을 기본으로 따름
- 일관성 있는 코드 스타일 유지

### 2. 가독성 우선
- 코드는 한 번만 작성되지만 여러 번 읽힘
- 명확하고 이해하기 쉬운 코드 작성

### 3. DRY (Don't Repeat Yourself)
- 중복 코드 제거
- 재사용 가능한 함수/클래스 작성

### 4. KISS (Keep It Simple, Stupid)
- 복잡한 로직보다는 간단하고 명확한 로직 선호
- 과도한 추상화 지양

## 코드 스타일

### 들여쓰기
```python
# 올바른 예
def function_name():
    if condition:
        do_something()
    else:
        do_something_else()

# 잘못된 예
def function_name():
  if condition:
      do_something()
  else:
      do_something_else()
```

### 줄 길이
- 최대 79자 (PEP 8 권장)
- 긴 줄은 적절히 분리

```python
# 긴 줄 분리 예시
long_function_name(
    parameter1,
    parameter2,
    parameter3
)

# 문자열 연결
long_string = (
    "This is a very long string that "
    "needs to be split across multiple lines"
)
```

### 공백 사용
```python
# 올바른 예
spam(ham[1], {eggs: 2})
foo = (0,)

# 잘못된 예
spam( ham[ 1 ], { eggs: 2 } )
foo = (0, )
```

### 임포트 순서
```python
# 표준 라이브러리
import os
import sys
from datetime import datetime

# 서드파티 라이브러리
import numpy as np
import pandas as pd

# 로컬 애플리케이션/라이브러리
from .models import User
from .utils import helper_function
```

## 네이밍 컨벤션

### 변수명
```python
# 스네이크 케이스 사용
user_name = "홍길동"
total_count = 100
is_valid = True

# 상수는 대문자
MAX_RETRY_COUNT = 3
DEFAULT_TIMEOUT = 30
```

### 함수명
```python
# 동사로 시작하는 스네이크 케이스
def get_user_info():
    pass

def calculate_total_price():
    pass

def is_valid_email(email):
    pass
```

### 클래스명
```python
# 파스칼 케이스 사용
class UserManager:
    pass

class DatabaseConnection:
    pass

class EmailValidator:
    pass
```

### 모듈명
```python
# 소문자 스네이크 케이스
user_management.py
database_utils.py
email_service.py
```

## 문서화

### Docstring 작성
```python
def calculate_monthly_salary(hourly_wage: float, hours_worked: int) -> float:
    """
    월급을 계산합니다.
    
    Args:
        hourly_wage (float): 시급 (원)
        hours_worked (int): 근무 시간 (시간)
    
    Returns:
        float: 월급 (원)
    
    Raises:
        ValueError: 시급이나 근무시간이 음수인 경우
    
    Example:
        >>> calculate_monthly_salary(10000, 160)
        1600000.0
    """
    if hourly_wage < 0 or hours_worked < 0:
        raise ValueError("시급과 근무시간은 0 이상이어야 합니다.")
    
    return hourly_wage * hours_worked
```

### 클래스 Docstring
```python
class Worker:
    """
    일용근로자 정보를 관리하는 클래스.
    
    Attributes:
        name (str): 근로자 이름
        id_number (str): 주민등록번호
        phone (str): 휴대전화번호
        team (str): 소속팀
        bank_account (str): 계좌번호
        safety_training (bool): 안전교육 이수 여부
        notes (str): 비고사항
    """
    
    def __init__(self, name: str, id_number: str):
        self.name = name
        self.id_number = id_number
        # ... 기타 초기화
```

### 주석 작성
```python
# 좋은 주석 예시
def validate_id_number(id_number: str) -> bool:
    # 주민등록번호 형식 검증 (000000-0000000)
    if not re.match(r'^\d{6}-\d{7}$', id_number):
        return False
    
    # 체크섬 검증
    digits = id_number.replace('-', '')
    weights = [2, 3, 4, 5, 6, 7, 2, 3, 4, 5, 6, 7]
    
    checksum = sum(int(d) * w for d, w in zip(digits[:-1], weights))
    check_digit = (11 - (checksum % 11)) % 10
    
    return int(digits[-1]) == check_digit
```

## 에러 처리

### 예외 처리 원칙
```python
# 구체적인 예외 처리
try:
    with open(file_path, 'r') as file:
        data = file.read()
except FileNotFoundError:
    logger.error(f"파일을 찾을 수 없습니다: {file_path}")
    raise
except PermissionError:
    logger.error(f"파일 접근 권한이 없습니다: {file_path}")
    raise
except Exception as e:
    logger.error(f"예상치 못한 오류: {e}")
    raise

# 사용자 정의 예외
class WorkerNotFoundError(Exception):
    """근로자를 찾을 수 없을 때 발생하는 예외"""
    pass

class InvalidDataError(Exception):
    """잘못된 데이터 형식일 때 발생하는 예외"""
    pass
```

### 컨텍스트 매니저 사용
```python
# 파일 처리
with open('data.txt', 'r', encoding='utf-8') as file:
    content = file.read()

# 데이터베이스 연결
with database_connection() as conn:
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM workers")
```

## 성능 최적화

### 리스트 컴프리헨션 활용
```python
# 좋은 예
squares = [x**2 for x in range(10) if x % 2 == 0]

# 나쁜 예
squares = []
for x in range(10):
    if x % 2 == 0:
        squares.append(x**2)
```

### 제너레이터 사용
```python
def read_large_file(file_path: str):
    """대용량 파일을 메모리 효율적으로 읽기"""
    with open(file_path, 'r') as file:
        for line in file:
            yield line.strip()

# 사용
for line in read_large_file('large_data.txt'):
    process_line(line)
```

### 적절한 자료구조 선택
```python
# 검색이 많은 경우
workers_dict = {worker.id: worker for worker in workers}

# 순서가 중요한 경우
from collections import OrderedDict
ordered_workers = OrderedDict()

# 중복 제거가 필요한 경우
unique_teams = set(worker.team for worker in workers)
```

## 보안

### 입력 검증
```python
import re
from typing import Optional

def validate_phone_number(phone: str) -> bool:
    """휴대전화번호 형식 검증"""
    pattern = r'^01[0-9]-\d{3,4}-\d{4}$'
    return bool(re.match(pattern, phone))

def sanitize_input(user_input: str) -> str:
    """사용자 입력 정제"""
    # HTML 태그 제거
    import html
    return html.escape(user_input.strip())
```

### 민감 정보 처리
```python
import os
from cryptography.fernet import Fernet

class SecureStorage:
    """민감 정보 암호화 저장"""
    
    def __init__(self):
        self.key = os.getenv('ENCRYPTION_KEY')
        self.cipher = Fernet(self.key)
    
    def encrypt(self, data: str) -> bytes:
        return self.cipher.encrypt(data.encode())
    
    def decrypt(self, encrypted_data: bytes) -> str:
        return self.cipher.decrypt(encrypted_data).decode()
```

## 테스트

### 단위 테스트 작성
```python
import unittest
from unittest.mock import patch, MagicMock

class TestWorkerManager(unittest.TestCase):
    
    def setUp(self):
        """테스트 전 설정"""
        self.worker_manager = WorkerManager()
        self.sample_worker = Worker("홍길동", "123456-1234567")
    
    def test_add_worker(self):
        """근로자 추가 테스트"""
        result = self.worker_manager.add_worker(self.sample_worker)
        self.assertTrue(result)
        self.assertIn(self.sample_worker, self.worker_manager.workers)
    
    def test_validate_id_number(self):
        """주민등록번호 검증 테스트"""
        valid_id = "123456-1234567"
        invalid_id = "123456-1234568"
        
        self.assertTrue(validate_id_number(valid_id))
        self.assertFalse(validate_id_number(invalid_id))
    
    @patch('builtins.open', create=True)
    def test_save_to_file(self, mock_open):
        """파일 저장 테스트"""
        mock_file = MagicMock()
        mock_open.return_value.__enter__.return_value = mock_file
        
        self.worker_manager.save_to_file("test.txt")
        mock_file.write.assert_called()
```

### 테스트 커버리지
```python
# pytest-cov 사용
# pytest --cov=src --cov-report=html

# 최소 80% 커버리지 유지
```

## 프로젝트 구조

```
dlm/
├── src/
│   ├── __init__.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── worker.py
│   │   └── team.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── worker_service.py
│   │   └── file_service.py
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── validators.py
│   │   └── helpers.py
│   └── main.py
├── tests/
│   ├── __init__.py
│   ├── test_models/
│   ├── test_services/
│   └── test_utils/
├── docs/
├── requirements.txt
├── setup.py
└── README.md
```

## 코드 리뷰 체크리스트

- [ ] PEP 8 준수 여부
- [ ] 적절한 네이밍 컨벤션 사용
- [ ] Docstring 작성 여부
- [ ] 예외 처리 적절성
- [ ] 테스트 코드 작성 여부
- [ ] 보안 고려사항
- [ ] 성능 최적화
- [ ] 코드 중복 제거
- [ ] 가독성 확인

## 도구 설정

### pre-commit hooks
```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/psf/black
    rev: 22.3.0
    hooks:
      - id: black
        language_version: python3
  
  - repo: https://github.com/pycqa/flake8
    rev: 4.0.1
    hooks:
      - id: flake8
  
  - repo: https://github.com/pycqa/isort
    rev: 5.10.1
    hooks:
      - id: isort
```

### IDE 설정
- VS Code: Python 확장 설치
- PyCharm: 코드 스타일 설정
- Black, isort, flake8 자동 포맷팅 설정

이 규칙들을 따르면 일관성 있고 유지보수하기 쉬운 코드를 작성할 수 있습니다. 