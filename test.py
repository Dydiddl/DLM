import math

n = 22
w = 6
num = 8

print("박스 분류를 시작합니다.")
print("총 {}개의 택배 상자가 있습니다.".format(n))
print("가로 상자 개수는 {}개입니다.".format(w))
print("꺼낼 상자 번호는 {}번입니다.".format(num))

# 층 계산
for f in range(1, math.ceil(n/w) + 1): 
    # 만약 n= 22, w= 6이면 3.xxx라는 값이 나와서 4층이 있는 곳도 있고, 3층까지 있는 곳이 있을 수 있음
    # 그래서 3.xxx 나오게 되면 올림을 해서 층을 계산
    if (f-1) * w < num <= f * w:
        floor = f
        print("{}층에 있는 상자입니다.".format(floor))
        break

# 추출할 상자 위치 계산
if floor % 2 == 0:
    print("짝수층입니다. 짝수층은 오른쪽부터(x 번째부터) 계산합니다.")
    index_num = w - (num % w) + 1
    print("꺼내야 하는 상자는 오른쪽에서 {}번째 상자입니다.".format(index_num))
else:
    print("홀수층입니다. 홀수층은 왼쪽부터(x 번째부터) 계산합니다.")
    index_num = num % w
    print("꺼내야 하는 상자는 왼쪽에서 {}번째 상자입니다.".format(index_num))

# 추출할 상자의 1층부터 끝층까지의 상자 번호 계산
# 
print("num이 포함된 열의 박스 번호를 계산하겠습니다.")
print("num이 포함된 층은" + str(floor) + "층입니다.")
max_floor = 0
for m in range(1, math.ceil(n/w) + 1):
    # num이 있는 층이 홀수 일때
    if floor % 2 != 0:
        if m % 2 != 0:
            print("검사: floor 홀수" + str(m))
            box_calculation = ((m-1) * w) + index_num # 각층의 좌표를 계산하고
            print(box_calculation)
            if 1 <= box_calculation <= n:
                max_floor += 1
            else:
                max_floor += 0
        else:
            print("검사: floor 홀수" + str(m))
            box_calculation = (((m-1) * w) + (w+1-index_num)) # 각층의 좌표를 계산하고
            print(box_calculation)
            if 1 <= box_calculation <= n:
                max_floor += 1
            else:
                max_floor += 0
    # num이 있는 층이 짝수 일때
    if floor % 2 == 0:
        if m % 2 == 0: # 짝수층일때
            print("검사: floor 짝수" + str(m))
            box_calculation = (((m-1) * w) + index_num) # 각층의 좌표를 계산하고
            print(box_calculation)
            if 1 <=box_calculation <= n:
                max_floor += 1
            else:
                max_floor += 0
        else: # 홀수층일때 
            print("검사: floor 짝수" + str(m))
            box_calculation = ((m - 1) * w) + (w + 1 - index_num) # 각층의 좌표를 계산하고
            print(box_calculation)
            if 1 <=box_calculation <= n:
                max_floor += 1
            else:
                max_floor += 0
        

# result 계산
print(max_floor)

