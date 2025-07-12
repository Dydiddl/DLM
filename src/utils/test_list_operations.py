"""
리스트 연산 함수들의 테스트 케이스
"""

import unittest
from list_operations import solution, solution_optimized


class TestListOperations(unittest.TestCase):
    """리스트 연산 함수들의 테스트 클래스"""
    
    def test_solution_example_1(self):
        """입출력 예 #1 테스트"""
        num_list = [3, 4, 5, 2, 5, 4, 6, 7, 3, 7, 2, 2, 1]
        expected = 51
        self.assertEqual(solution(num_list), expected)
        self.assertEqual(solution_optimized(num_list), expected)
    
    def test_solution_example_2(self):
        """입출력 예 #2 테스트"""
        num_list = [2, 3, 4, 5]
        expected = 120
        self.assertEqual(solution(num_list), expected)
        self.assertEqual(solution_optimized(num_list), expected)
    
    def test_length_11_sum(self):
        """길이가 11일 때 합 계산 테스트"""
        num_list = [1, 2, 3, 4, 5, 6, 7, 8, 9, 1, 2]
        expected = 48
        self.assertEqual(solution(num_list), expected)
        self.assertEqual(solution_optimized(num_list), expected)
    
    def test_length_10_product(self):
        """길이가 10일 때 곱 계산 테스트"""
        num_list = [1, 2, 3, 4, 5, 6, 7, 8, 9, 1]
        expected = 362880  # 9! * 1
        self.assertEqual(solution(num_list), expected)
        self.assertEqual(solution_optimized(num_list), expected)
    
    def test_minimum_length(self):
        """최소 길이(2) 테스트"""
        num_list = [5, 6]
        expected = 30
        self.assertEqual(solution(num_list), expected)
        self.assertEqual(solution_optimized(num_list), expected)
    
    def test_maximum_length(self):
        """최대 길이(20) 테스트"""
        num_list = [1] * 20
        expected = 20  # 길이가 20이므로 합 계산
        self.assertEqual(solution(num_list), expected)
        self.assertEqual(solution_optimized(num_list), expected)
    
    def test_invalid_length_too_short(self):
        """길이가 너무 짧을 때 예외 발생 테스트"""
        with self.assertRaises(ValueError):
            solution([1])
    
    def test_invalid_length_too_long(self):
        """길이가 너무 길 때 예외 발생 테스트"""
        with self.assertRaises(ValueError):
            solution([1] * 21)
    
    def test_invalid_element_too_small(self):
        """원소가 너무 작을 때 예외 발생 테스트"""
        with self.assertRaises(ValueError):
            solution([1, 0])
    
    def test_invalid_element_too_large(self):
        """원소가 너무 클 때 예외 발생 테스트"""
        with self.assertRaises(ValueError):
            solution([1, 10])
    
    def test_invalid_input_type(self):
        """잘못된 입력 타입 예외 발생 테스트"""
        with self.assertRaises(ValueError):
            solution("not a list")  # type: ignore


if __name__ == "__main__":
    unittest.main() 