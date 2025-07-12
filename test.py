import math

n = 4
w = 1
num = 1

# num 이 포함된 층 계산
if num % w == 0:
    floor = num // w
else:
    floor = num // w + 1
# 최대 층 수 계산
if n % w == 0:
    max_floor = n // w
else:
    max_floor = n // w + 1
# num 이 포함된 줄의 꼭대기층에 상자의 유무
if max_floor % 2 != 0:
    if num % w == 0:
        if ((max_floor - 1) * w) + 1 <= n:
            pass
        else:
            max_floor -= 1
    else:
        if ((max_floor - 1) * w) + (num % w) <= n:
            pass
        else:
            max_floor -= 1
else:
    if num % w == 0:
        if ((max_floor - 1) * w) + 1 <= n:
            pass
        else:
            max_floor -= 1
    else:
        if ((max_floor - 1) * w) + (w - (num % w)) <= n:
            pass
        else:
            max_floor -= 1

answer = max_floor - floor + 1

print(floor)
print(max_floor)
print(answer)