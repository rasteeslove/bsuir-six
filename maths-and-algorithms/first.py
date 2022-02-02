import numpy as np

def optimul(A, B, index):
    # some checks and assertions could be here

    n = len(A)

    C = np.zeros([n, n])
    for i in range(n):
        for j in range(n):
            C[i][j] += A[i][index] * B[index][j]
            if i != index:
                C[i][j] += B[i][j]

    return C

def solution(A_minus_one, x, i):
    n = len(A_minus_one)

    # 1:
    l = A_minus_one @ x
    if l[i] == 0:
        return False

    # 2:
    l_wave = np.copy(l)
    l_wave[i] = -1.

    # 3:
    l_hat = -1.0/l[i] * l_wave

    # 4:
    Q = np.identity(n)
    for row in Q:
        row[i] = l_hat[i]

    # 5:
    A_dash_minus_one = optimul(Q, A_minus_one, i)

    return A_dash_minus_one

print(solution(np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]]), np.array([1, 1, 1]), 1))
