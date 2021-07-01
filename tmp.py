n = input("임의의 정수(1~9) 입력:")
for i in range(n):
    for j in range(n):
        if i >= j:
            print("j", end = "")
        else:
            print("*", end = "")
    print("")

