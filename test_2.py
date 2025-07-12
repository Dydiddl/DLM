import math

def solution(n, w, num):
    max_floor = 0
    floor = 0

    for f in range(1, math.ceil(n / w) + 1):
        if (f - 1) * w < num <= f * w:
            floor = f
            break

    for f in range(1, math.ceil(n / w) + 1):
        if f % 2 != 0: # 홀수층
            if num % w == 0: # 홀수층 첫시작은 +1 +2 씩 늘어남
                if ((f - 1) * w) + <= n:
                    max_floor += 1
                    print(str(max_floor) + str(f) + "1")
                else:
                    print(((f - 1) * w) + w)
                    max_floor += 0
                    print(str(max_floor) + str(f) + "1-1")
            else:
                if ((f - 1) * w) + (num % w) <= n:
                    max_floor += 1
                    print(((f - 1) * w) + (num % w))
                    print(str(max_floor) + str(f) + "2")
                else:
                    max_floor += 0
                    print(str(max_floor) + str(f) + "2-1")
        else: # 짝수층
            if num % w == 0:
                if ((f - 1) * w) + w <= n:
                    max_floor += 1
                    print(str(max_floor) + str(f) + "3")
                else:
                    max_floor += 0
                    print(str(max_floor) + str(f) + "3-1")
            else:
                if ((f - 1) * w) + (w - (num % w)) <= n:
                    max_floor += 1
                    print(str(max_floor) + str(f) + "4")
                else:
                    max_floor += 0
                    print(str(max_floor) + str(f) + "4-1")
    answer = max_floor - floor + 1
    print(floor)
    print(max_floor)
    return answer

print(solution(13,3,6))
