import math

def solution(n, w, num):
    answer = 0
    # n = 택배상재 개수 22
    # w = 가로 상자 개수 6
    # num = 꺼내야 하는 상자 번호 8
    # result = answer = 위에서 부터 꺼내야 하는 상자 개수 3

    max_floor = 0
    # 총 층수 구하는 함수
    for i in range(1, w + 1):


    # 현재 박스가 위치한 층수 구하는 함수
    for i in range(1, math.ceil(n/w) + 1): 
    # n=22, w=6 -> 3.6666나온다. 최대 층수는 4층인데, 반올림하고 4층까지 반복,
    #  range 함수는 1~5 를 표현하려면 range(1, 6) 이 되기때문에 +1 
        if num <= i * w:
            floor = i
            break


    answer = max_floor - floor + 1
   
    return answer

n = 22
w = 6
num = 8

print(solution(n, w, num))  # Expected output: 3

1 , 12 , 13 = 3층
2, 11, 14 = 3층
3, 10, 15, 22 = 4층
4, 9, 16, 21 = 4층
5, 8, 17, 20 = 4층
6, 7, 18, 19 = 4층


max_floor = 0
index = []
for i in range(1, n + 1):
    for c in range(1, w + 1):
        if i // c <= 1:
            this_floor = 1
        elif 

        index = ["{}-{}".format()]

[n층, 1번 열]
1층 = {[1-1, 1],[1-2, 2] 2, 3, 4, 5, 6}
2층 = {[2-1, 7], 8, 9, 10, 11, 12}



n층