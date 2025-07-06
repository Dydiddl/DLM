"""
경로 처리 유틸리티 모듈

윈도우와 맥 환경에서 경로를 일관되게 처리하기 위한 유틸리티 함수들을 제공합니다.
"""

import os
import pathlib
from typing import Union, Optional


def normalize_path(file_path: str) -> str:
    """
    윈도우 경로의 백슬래시를 슬래시로 변환하고 경로를 정규화합니다.
    
    Args:
        file_path (str): 변환할 파일 경로
        
    Returns:
        str: 정규화된 파일 경로
        
    Example:
        >>> normalize_path("D:\\Documents\\DLM\\data\\excel\\file.xlsx")
        'D:/Documents/DLM/data/excel/file.xlsx'
    """
    # 백슬래시를 슬래시로 변환
    normalized_path = file_path.replace('\\', '/')
    
    # pathlib을 사용하여 경로 정규화
    path_obj = pathlib.Path(normalized_path)
    return str(path_obj.resolve())


def convert_windows_path(windows_path: str) -> str:
    """
    윈도우 경로를 크로스 플랫폼 경로로 변환합니다.
    
    Args:
        windows_path (str): 윈도우 형식의 경로
        
    Returns:
        str: 변환된 경로
        
    Example:
        >>> convert_windows_path("D:\\Documents\\DLM\\file.xlsx")
        'D:/Documents/DLM/file.xlsx'
    """
    return windows_path.replace('\\', '/')


def ensure_directory_exists(file_path: str) -> str:
    """
    파일 경로의 디렉토리가 존재하지 않으면 생성합니다.
    
    Args:
        file_path (str): 파일 경로
        
    Returns:
        str: 정규화된 파일 경로
        
    Example:
        >>> ensure_directory_exists("D:/Documents/DLM/data/csv/file.csv")
        'D:/Documents/DLM/data/csv/file.csv'  # csv 디렉토리가 생성됨
    """
    normalized_path = normalize_path(file_path)
    directory = os.path.dirname(normalized_path)
    
    if directory and not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)
        print(f"디렉토리 생성: {directory}")
    
    return normalized_path


def get_file_extension(file_path: str) -> str:
    """
    파일 경로에서 확장자를 추출합니다.
    
    Args:
        file_path (str): 파일 경로
        
    Returns:
        str: 파일 확장자 (점 포함)
        
    Example:
        >>> get_file_extension("D:/Documents/file.xlsx")
        '.xlsx'
    """
    return pathlib.Path(file_path).suffix.lower()


def change_file_extension(file_path: str, new_extension: str) -> str:
    """
    파일 경로의 확장자를 변경합니다.
    
    Args:
        file_path (str): 원본 파일 경로
        new_extension (str): 새로운 확장자 (점 포함)
        
    Returns:
        str: 확장자가 변경된 파일 경로
        
    Example:
        >>> change_file_extension("D:/Documents/file.xlsx", ".csv")
        'D:/Documents/file.csv'
    """
    path_obj = pathlib.Path(normalize_path(file_path))
    return str(path_obj.with_suffix(new_extension))


def is_excel_file(file_path: str) -> bool:
    """
    파일이 엑셀 파일인지 확인합니다.
    
    Args:
        file_path (str): 파일 경로
        
    Returns:
        bool: 엑셀 파일 여부
        
    Example:
        >>> is_excel_file("D:/Documents/file.xlsx")
        True
        >>> is_excel_file("D:/Documents/file.csv")
        False
    """
    excel_extensions = {'.xlsx', '.xls', '.xlsm', '.xlsb'}
    return get_file_extension(file_path) in excel_extensions


def is_csv_file(file_path: str) -> bool:
    """
    파일이 CSV 파일인지 확인합니다.
    
    Args:
        file_path (str): 파일 경로
        
    Returns:
        bool: CSV 파일 여부
    """
    return get_file_extension(file_path) == '.csv'


def validate_file_path(file_path: str, required_extension: Optional[str] = None) -> tuple[bool, str]:
    """
    파일 경로를 검증합니다.
    
    Args:
        file_path (str): 검증할 파일 경로
        required_extension (str, optional): 필요한 확장자
        
    Returns:
        tuple[bool, str]: (유효성 여부, 오류 메시지)
        
    Example:
        >>> validate_file_path("D:/Documents/file.xlsx", ".xlsx")
        (True, "")
        >>> validate_file_path("D:/Documents/file.txt", ".xlsx")
        (False, "파일 확장자가 .xlsx가 아닙니다.")
    """
    normalized_path = normalize_path(file_path)
    
    # 파일 존재 여부 확인
    if not os.path.exists(normalized_path):
        return False, f"파일이 존재하지 않습니다: {normalized_path}"
    
    # 파일인지 확인 (디렉토리가 아닌)
    if not os.path.isfile(normalized_path):
        return False, f"파일이 아닙니다: {normalized_path}"
    
    # 확장자 검증
    if required_extension:
        actual_extension = get_file_extension(normalized_path)
        if actual_extension != required_extension.lower():
            return False, f"파일 확장자가 {required_extension}가 아닙니다. (현재: {actual_extension})"
    
    return True, ""


def get_relative_path(base_path: str, target_path: str) -> str:
    """
    기준 경로에 대한 상대 경로를 계산합니다.
    
    Args:
        base_path (str): 기준 경로
        target_path (str): 대상 경로
        
    Returns:
        str: 상대 경로
        
    Example:
        >>> get_relative_path("D:/Documents/DLM", "D:/Documents/DLM/data/file.xlsx")
        'data/file.xlsx'
    """
    base = pathlib.Path(normalize_path(base_path))
    target = pathlib.Path(normalize_path(target_path))
    return str(target.relative_to(base))


def create_backup_path(original_path: str, backup_suffix: str = "_backup") -> str:
    """
    원본 파일의 백업 경로를 생성합니다.
    
    Args:
        original_path (str): 원본 파일 경로
        backup_suffix (str): 백업 파일 접미사
        
    Returns:
        str: 백업 파일 경로
        
    Example:
        >>> create_backup_path("D:/Documents/file.xlsx")
        'D:/Documents/file_backup.xlsx'
    """
    path_obj = pathlib.Path(normalize_path(original_path))
    backup_name = f"{path_obj.stem}{backup_suffix}{path_obj.suffix}"
    return str(path_obj.parent / backup_name) 