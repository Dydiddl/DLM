# 윈도우 경로 처리 가이드

## 개요

윈도우 환경에서 파일 경로를 복사할 때 백슬래시(`\`)가 사용되지만, 파이썬에서는 슬래시(`/`)를 사용하는 것이 권장됩니다. 이 문서는 윈도우 경로를 올바르게 처리하는 방법을 설명합니다.

## 문제 상황

윈도우에서 파일 경로를 복사하면 다음과 같은 형태가 됩니다:
```
D:\Documents\DLM\data\excel\DayLabolList.xlsx
```

하지만 파이썬에서는 다음과 같은 형태를 사용해야 합니다:
```
D:/Documents/DLM/data/excel/DayLabolList.xlsx
```

## 해결 방법

### 1. normalize_path() 함수 사용 (권장)

```python
from src.utils.path_utils import normalize_path

# 윈도우에서 복사한 경로
windows_path = "D:\\Documents\\DLM\\data\\excel\\DayLabolList.xlsx"

# 정규화된 경로로 변환
normalized_path = normalize_path(windows_path)
print(normalized_path)
# 출력: D:/Documents/DLM/data/excel/DayLabolList.xlsx
```

### 2. convert_windows_path() 함수 사용

```python
from src.utils.path_utils import convert_windows_path

# 윈도우 경로 변환
converted_path = convert_windows_path(windows_path)
print(converted_path)
# 출력: D:/Documents/DLM/data/excel/DayLabolList.xlsx
```

### 3. 수동 변환

```python
# 백슬래시를 슬래시로 직접 변환
path = "D:\\Documents\\DLM\\file.xlsx".replace('\\', '/')
print(path)
# 출력: D:/Documents/DLM/file.xlsx
```

## 제공되는 유틸리티 함수들

### 경로 정규화
- `normalize_path(file_path)`: 경로를 정규화하고 절대 경로로 변환
- `convert_windows_path(windows_path)`: 윈도우 경로를 크로스 플랫폼 경로로 변환

### 파일 검증
- `validate_file_path(file_path, required_extension)`: 파일 경로 검증
- `is_excel_file(file_path)`: 엑셀 파일 여부 확인
- `is_csv_file(file_path)`: CSV 파일 여부 확인

### 경로 조작
- `change_file_extension(file_path, new_extension)`: 파일 확장자 변경
- `ensure_directory_exists(file_path)`: 디렉토리 존재 확인 및 생성
- `get_file_extension(file_path)`: 파일 확장자 추출

## 사용 예시

### 엑셀 파일을 CSV로 변환

```python
from src.utils.pandas.excel_to_CSV import excel_to_CSV
from src.utils.path_utils import normalize_path

# 윈도우에서 복사한 경로
excel_path = "D:\\Documents\\DLM\\data\\excel\\DayLabolList.xlsx"

# 경로 정규화
normalized_excel_path = normalize_path(excel_path)
csv_path = "D:/Documents/DLM/data/csv/DayLabolList.csv"

# 변환 실행
success = excel_to_CSV(normalized_excel_path, csv_path)
```

### 대화형 파일 경로 입력

```python
from src.utils.pandas.excel_to_CSV import get_file_path

# 사용자로부터 경로 입력 받기 (자동으로 정규화됨)
file_path = get_file_path()
print(f"입력된 경로: {file_path}")
```

## 주의사항

1. **경로 구분자**: 윈도우에서는 `\`와 `/` 모두 사용 가능하지만, 파이썬에서는 `/` 사용을 권장
2. **절대 경로**: `normalize_path()` 함수는 상대 경로를 절대 경로로 변환
3. **파일 존재 확인**: `validate_file_path()` 함수로 파일 존재 여부 확인
4. **디렉토리 생성**: `ensure_directory_exists()` 함수로 필요한 디렉토리 자동 생성

## 테스트 실행

경로 유틸리티 함수들을 테스트하려면:

```bash
cd src/utils
python test_path_utils.py
```

## 관련 파일

- `src/utils/path_utils.py`: 경로 처리 유틸리티 함수들
- `src/utils/pandas/excel_to_CSV.py`: 엑셀 to CSV 변환 (경로 처리 포함)
- `src/utils/test_path_utils.py`: 경로 유틸리티 테스트
- `docs/windows_path_handling.md`: 이 문서 