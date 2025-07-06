"""
경로 유틸리티 테스트 및 사용 예시

윈도우 경로 처리 기능을 테스트하고 사용법을 보여줍니다.
"""

from path_utils import (
    normalize_path,
    convert_windows_path,
    ensure_directory_exists,
    change_file_extension,
    validate_file_path,
    is_excel_file,
    is_csv_file
)


def test_windows_path_conversion():
    """윈도우 경로 변환 테스트"""
    print("=== 윈도우 경로 변환 테스트 ===")
    
    # 윈도우에서 복사한 경로 예시
    windows_paths = [
        "D:\\Documents\\DLM\\data\\excel\\DayLabolList.xlsx",
        "C:\\Users\\User\\Desktop\\work\\file.xls",
        "E:\\Backup\\2024\\data\\report.xlsx"
    ]
    
    for path in windows_paths:
        normalized = normalize_path(path)
        converted = convert_windows_path(path)
        
        print(f"원본: {path}")
        print(f"정규화: {normalized}")
        print(f"변환: {converted}")
        print("-" * 50)


def test_file_validation():
    """파일 검증 테스트"""
    print("\n=== 파일 검증 테스트 ===")
    
    test_paths = [
        "D:/Documents/DLM/data/excel/DayLabolList.xlsx",
        "D:/Documents/DLM/data/csv/DayLabolList.csv",
        "D:/Documents/DLM/data/txt/readme.txt"
    ]
    
    for path in test_paths:
        # 엑셀 파일 검증
        is_excel = is_excel_file(path)
        is_csv = is_csv_file(path)
        
        # 경로 검증
        is_valid, error_msg = validate_file_path(path)
        
        print(f"경로: {path}")
        print(f"  엑셀 파일: {is_excel}")
        print(f"  CSV 파일: {is_csv}")
        print(f"  유효한 경로: {is_valid}")
        if not is_valid:
            print(f"  오류: {error_msg}")
        print("-" * 30)


def test_extension_change():
    """확장자 변경 테스트"""
    print("\n=== 확장자 변경 테스트 ===")
    
    original_path = "D:/Documents/DLM/data/excel/DayLabolList.xlsx"
    
    # CSV로 변경
    csv_path = change_file_extension(original_path, ".csv")
    print(f"원본: {original_path}")
    print(f"CSV: {csv_path}")
    
    # TXT로 변경
    txt_path = change_file_extension(original_path, ".txt")
    print(f"TXT: {txt_path}")


def test_directory_creation():
    """디렉토리 생성 테스트"""
    print("\n=== 디렉토리 생성 테스트 ===")
    
    # 존재하지 않는 디렉토리를 포함한 경로
    test_path = "D:/Documents/DLM/data/new_folder/test.csv"
    
    try:
        result_path = ensure_directory_exists(test_path)
        print(f"원본 경로: {test_path}")
        print(f"결과 경로: {result_path}")
        print("디렉토리가 생성되었습니다.")
    except Exception as e:
        print(f"오류 발생: {e}")


def main():
    """메인 테스트 함수"""
    print("경로 유틸리티 테스트 시작\n")
    
    # 각 테스트 실행
    test_windows_path_conversion()
    test_file_validation()
    test_extension_change()
    test_directory_creation()
    
    print("\n=== 사용 예시 ===")
    print("윈도우에서 경로를 복사했을 때:")
    print("1. normalize_path() 함수 사용")
    print("2. convert_windows_path() 함수 사용")
    print("3. validate_file_path() 함수로 검증")
    print("4. ensure_directory_exists() 함수로 디렉토리 생성")
    
    print("\n예시:")
    print("windows_path = 'D:\\Documents\\DLM\\file.xlsx'")
    print("normalized = normalize_path(windows_path)")
    print("결과: 'D:/Documents/DLM/file.xlsx'")


if __name__ == "__main__":
    main() 