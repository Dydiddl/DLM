import math

def solution(n, w, num):
    # 층 계산
    for f in range(1, math.ceil(n / w) + 1): 
        if (f-1) * w < num <= f * w:
            floor = f
            break
    # 추출할 상자 위치 계산
    if floor % 2 == 0:
        if num % w == 0:
            index_num = w
        else:
            index_num = num % w
    else:
        if num % w == 0:
            index_num = w 
        elif floor == 1:
            index_num = num
        else:
            index_num = w - (num % w) + 1

    max_floor = 0
    for m in range(1, math.ceil(n / w) + 1):
        if m % 2 != 0:
            if index_num == w:
                box_num = w
                if 1 <= box_num <= n:
                    max_floor += 1
                else:
                    max_floor += 0
            elif floor == 1:
                box_num = num
                max_floor += 1
            else:
                box_num = ((m - 1) * w) + (w + 1 - index_num) # 각층의 좌표를 계산하고
                if 1 <= box_num <= n:
                    max_floor += 1
                else:
                    max_floor += 0
        else:
            if index_num == w:
                box_num = w
                if 1 <= box_num <= n:
                    max_floor += 1
                else:
                    max_floor += 0
            elif floor == 1:
                max_floor += 0
            else:
                box_num = (((m - 1) * w) + index_num) # 각층의 좌표를 계산하고
                if 1 <= box_num <= n:
                    max_floor += 1
                else:
                    max_floor += 0
    answer = max_floor - floor + 1    

    return answer


print(solution(12,11,1))