import math

n = 22
w = 6
num = 4

print("박스 분류를 시작합니다.")
print("총 {}개의 택배 상자가 있습니다.".format(n))
print("가로 상자 개수는 {}개입니다.".format(w))
print("꺼낼 상자 번호는 {}번입니다.".format(num))

# 층 계산
for f in range(1, math.ceil(n/w) + 1): 
    # 만약 n= 22, w= 6이면 3.xxx 나와서 4층이 있는 곳도 있고, 3층까지 있는 곳이 있을 수 있음
    # 그래서 3.xxx 나오게 되면 올림을 해서 층을 계산
    if (f-1) * w <num <= f * w:
        floor = f
        print("{}층에 있는 상자입니다.".format(floor))
        break

# 추출할 상자 위치 계산
if floor % 2 == 0:
    print("짝수층입니다. 짝수층은 오른쪽부터(x 번째부터) 계산합니다.")
    index_num = num % w
    print("꺼내야 하는 상자는 오른쪽에서 {}번째 상자입니다.".format(index_num))
else:
    print("홀수층입니다. 홀수층은 왼쪽부터(x 번째부터) 계산합니다.")
    index_num = num % w
    print("꺼내야 하는 상자는 왼쪽에서 {}번째 상자입니다.".format(index_num))

# 추출할 상자의 1층부터 끝층까지의 상자 번호 계산
# 기준이 되는 상자 번호 num의 번호는 index_num -> 만약 index_num이 오른쪽 2라면, 왼쪽값은 5, w-index_num
# 1->6, 2->5, 3->4, 4->3, 5->2, 6->1 따라서 w+1-index_num, 그럼 1번값이라면, 
# 1층 왼쪽에서부터 5번째, 2층 오른쪽 2번째 상자 -> 3층 -> 왼쪽에서 5번째, 
# 1층의 왼쪽에서 부터 5번째는, 1부터 시작  -> 1 * index_num = 5
# 2층의 오른쪽에서 2번째는 w+1 부터 시작 -> 2(층수, m) * w +
# 3층의 왼쪽에서 부터 5번째는 2W+1 부터 시작
# 4층의 오른쪽에서 2번째는 3W+1 부터 시작
# 1층 index_num 1, 2층은 6, 그러면 w - index_num + 1

print("num이 포함된 열의 박스 번호를 계산하겠습니다.")
print("num이 포함된 층은" + str(floor) + "층입니다.")
max_floor = 0
for m in range(1, math.ceil(n/w) + 1):
    # num이 있는 층이 홀수 일때
    if floor % 2 != 0:
        if m % 2 == 0:
            print("검사: floor 홀수" + str(m))
            box_calculation = ((m-1) * w) + index_num # 각층의 좌표를 계산하고
            print(box_calculation)
            if 1 <=box_calculation <= n:
                max_floor += 1
            else:
                max_floor += 0
        else:
            print("검사: floor 홀수" + str(m))
            box_calculation = ((m-1 * w) + (w+1-index_num)) # 각층의 좌표를 계산하고
            print(box_calculation)
            if 1 <=box_calculation <= n:
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
            box_calculation = ((m - 1 * w) + (w + 1 - index_num)) # 각층의 좌표를 계산하고
            print(box_calculation)
            if 1 <=box_calculation <= n:
                max_floor += 1
            else:
                max_floor += 0
        

# result 계산
print(max_floor)

