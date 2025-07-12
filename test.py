import math

n = 22
w = 6
num = 4

print("박스 분류를 시작합니다.")
print("총 {}개의 택배 상자가 있습니다.".format(n))
print("가로 상자 개수는 {}개입니다.".format(w))
print("꺼낼 상자 번호는 {}번입니다.".format(num))


for f in range(1, math.ceil(n/w) + 1): 
    if num <= f * w:
        floor = f
        print("{}층에 있는 상자입니다.".format(floor))
        break

if floor % 2 == 0:
    print("짝수층입니다. 짝수층은 오른쪽부터(w번째부터) 계산합니다.")
    index_num = (num // w) + 1
    print("꺼내야 하는 상자는 오른쪽에서 {}번째 상자입니다.".format(index_num))
else:
    print("홀수층입니다. 홀수층은 왼쪽부터(1번째부터) 계산합니다.")
    index_num = (num // w) + 1
    print("꺼내야 하는 상자는 왼쪽에서 {}번째 상자입니다.".format(index_num))


