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

def solution(A_minus_one, x, index):
    n = len(A_minus_one)

    # 1:
    l = A_minus_one @ x
    if l[index] == 0:
        return False

    # 2:
    l_wave = np.copy(l)
    l_wave[index] = -1.

    # 3:
    l_hat = -1.0/l[index] * l_wave

    # 4:
    Q = np.identity(n)
    for i in range(len(Q)):
        Q[i][index] = l_hat[i]

    # 5:
    A_dash_minus_one = optimul(Q, A_minus_one, index)

    return A_dash_minus_one

# print(14 * solution(np.array([[-24, 20, -5], [18, -15, 4], [5, -4, 1]]), np.array([2, 2, 2]), 1))
# desired output: [[-12, 10, 2],[18, -15, 4],[-2, 4, -2]]
