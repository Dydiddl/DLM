import os

import pandas as pd

from ..path_utils import (
    normalize_path,
    ensure_directory_exists,
    change_file_extension,
    validate_file_path,
    is_excel_file
)

def get_file_path() -> str:
    """사용자로부터 파일 경로 입력받기"""
    while True:
        file_path = input("파일 경로를 입력하세요: ").strip()
        
        # 경로 검증
        is_valid, error_message = validate_file_path(file_path, ".xlsx")
        
        if is_valid:
            normalized_path = normalize_path(file_path)
            print(f"정규화된 경로: {normalized_path}")
            return normalized_path
        else:
            print(f"오류: {error_message}")
            print("다시 입력하세요.")

def excel_to_CSV(excel_file_path: str, csv_file_path: str, sheet_name: str = "일용직목록"):
    """
    엑셀 파일을 CSV 파일로 변환하는 함수
    
    Args:
        excel_file_path (str): 엑셀 파일 경로
        csv_file_path (str): 저장할 CSV 파일 경로
        sheet_name (str): 읽을 시트 이름 (기본값: "일용직목록")
        
    Returns:
        bool: 변환 성공 여부
    """
    try:
        # 엑셀 파일 검증
        if not is_excel_file(excel_file_path):
            print("오류: 엑셀 파일이 아닙니다.")
            return False
        
        # 경로 정규화 및 디렉토리 생성
        excel_file_path = normalize_path(excel_file_path)
        csv_file_path = ensure_directory_exists(csv_file_path)
        
        # 엑셀 파일 읽기
        df = pd.read_excel(excel_file_path, sheet_name=sheet_name)
        
        # CSV 파일로 저장
        df.to_csv(csv_file_path, index=False, encoding="utf-8-sig")
        
        print(f"엑셀 파일이 CSV 파일로 변환되었습니다: {csv_file_path}")
        print(f"변환된 파일 크기: {os.path.getsize(csv_file_path) / (1024 * 1024):.2f}MB")
        print(f"변환된 파일 행 수: {len(df)}")
        print(f"변환된 파일 열 수: {len(df.columns)}")
        print(f"변환된 파일 첫 번째 행: {df.head(1)}")
        print(f"변환된 파일 마지막 행: {df.tail(1)}")
        
        return True
    except Exception as e:
        print(f"오류 발생: {e}")
        return False

def main():
    """메인 실행 함수"""
    print("=== 엑셀 파일을 CSV로 변환하는 프로그램 ===")
    
    # 엑셀 파일 경로 입력
    excel_path = get_file_path()
    
    # CSV 파일 경로 생성
    csv_path = change_file_extension(excel_path, ".csv")
    
    # 변환 실행
    success = excel_to_CSV(excel_path, csv_path)
    
    if success:
        print("변환이 완료되었습니다!")
    else:
        print("변환 중 오류가 발생했습니다.")

if __name__ == "__main__":
    main()