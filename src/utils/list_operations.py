"""
리스트 연산 관련 유틸리티 함수들
"""

from typing import List


def solution(num_list: List[int]) -> int:
    """
    리스트의 길이에 따라 모든 원소의 합 또는 곱을 반환합니다.
    
    Args:
        num_list (List[int]): 정수가 담긴 리스트 (길이 2-20, 원소 1-9)
    
    Returns:
        int: 리스트 길이가 11 이상이면 모든 원소의 합, 10 이하이면 모든 원소의 곱
    
    Raises:
        ValueError: 입력 리스트가 제한사항을 만족하지 않을 때
    
    Example:
        >>> solution([3, 4, 5, 2, 5, 4, 6, 7, 3, 7, 2, 2, 1])
        51
        >>> solution([2, 3, 4, 5])
        120
    """
    # 입력 검증
    if not isinstance(num_list, list):
        raise ValueError("num_list는 리스트여야 합니다.")
    
    if len(num_list) < 2 or len(num_list) > 20:
        raise ValueError("리스트의 길이는 2 이상 20 이하여야 합니다.")
    
    for num in num_list:
        if not isinstance(num, int) or num < 1 or num > 9:
            raise ValueError("리스트의 모든 원소는 1 이상 9 이하의 정수여야 합니다.")
    
    # 리스트 길이에 따라 연산 결정
    if len(num_list) >= 11:
        # 길이가 11 이상이면 모든 원소의 합
        return sum(num_list)
    else:
        # 길이가 10 이하이면 모든 원소의 곱
        result = 1
        for num in num_list:
            result *= num
        return result


def solution_optimized(num_list: List[int]) -> int:
    """
    최적화된 버전의 solution 함수 (math.prod 사용)
    
    Args:
        num_list (List[int]): 정수가 담긴 리스트 (길이 2-20, 원소 1-9)
    
    Returns:
        int: 리스트 길이가 11 이상이면 모든 원소의 합, 10 이하이면 모든 원소의 곱
    """
    import math
    
    # 입력 검증
    if not isinstance(num_list, list):
        raise ValueError("num_list는 리스트여야 합니다.")
    
    if len(num_list) < 2 or len(num_list) > 20:
        raise ValueError("리스트의 길이는 2 이상 20 이하여야 합니다.")
    
    for num in num_list:
        if not isinstance(num, int) or num < 1 or num > 9:
            raise ValueError("리스트의 모든 원소는 1 이상 9 이하의 정수여야 합니다.")
    
    # 리스트 길이에 따라 연산 결정
    if len(num_list) >= 11:
        return sum(num_list)
    else:
        return math.prod(num_list) 