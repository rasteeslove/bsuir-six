"""
Решение матричной транспортной задачи с помощью метода потенциалов.
"""

import copy
import numpy as np
from collections import Counter


# the max number of iterations to attempt:
MAX_ITER = 42


def nw_corner_method(a, b):
    """
    Метод северо-западного угла.

    INPUT:
    - a
    - b

    OUTPUT:
    - X
    - B
    """
    a = copy.deepcopy(a)
    b = copy.deepcopy(b)

    n = len(a)
    m = len(b)

    X = np.zeros((n, m))
    B = []

    i = 0
    j = 0
    while True:
        B.append((i, j))

        if a[i] > 0 and b[j] > 0:
            if a[i] > b[j]:
                a[i] -= b[j]
                X[i][j] = b[j]
                b[j] = 0
                j += 1
            else:
                b[j] -= a[i]
                X[i][j] = a[i]
                a[i] = 0
                i += 1
        elif a[i] == 0:
            i += 1
        else:
            j += 1

        if i == n or j == m:
            break
    
    assert len(B) == n + m - 1

    return X, B


def solve(a: np.array, b: np.array, C: np.array):
    """
    Метод потенциалов решения матричной транспортной задачи.

    INPUT:
    - a
    - b
    - C

    OUTPUT: (tuple)
    - solved
    - X
    """
    assert all([el >= 0 for el in a])
    assert all([el >= 0 for el in b])
    assert all([el >= 0 for el in C.flatten()])

    diff = np.sum(a) - np.sum(b)
    if diff > 0:
        b.append(diff)
        C = [[C[i][j] if j < n else 0 for j in range(n+1)] for i in range(m)]
    elif diff < 0:
        a.append(-diff)
        C = [C[i] if i < m else np.zeros(n) for i in range(m+1)]

    m = len(a)
    n = len(b)

    X, B = nw_corner_method(a, b)

    for i in range(MAX_ITER):
        # 1, 2:
        A = np.zeros((m+n, m+n))
        b = np.zeros(m+n)
        for num, (i, j) in enumerate(B):
            A[num][i] = 1
            A[num][m+j] = 1
            b[num] = C[i][j]
        A[-1][0] = 1

        # 3:
        u_v = np.linalg.solve(A, b)
        u = u_v[:m]
        v = u_v[m:]

        # 4, 5:
        nB = []
        for i in range(m):
            for j in range(n):
                if (i, j) not in B:
                    nB.append((i, j))

        optimal_condition_met = True
        for (i, j) in nB:
            if u[i] + v[j] > C[i][j]:
                optimal_condition_met = False
                break
        if optimal_condition_met:  # 4
            return True, X
        B.append((i, j))  # 5

        # 6:
        B_copy = B.copy()
        while True:
            i_list = [i for (i, j) in B_copy]
            j_list = [j for (i, j) in B_copy]
            i_counter = Counter(i_list)
            j_counter = Counter(j_list)
            i_to_rm = [i for i in i_counter if i_counter[i] == 1]
            j_to_rm = [j for j in j_counter if j_counter[j] == 1]
            if not i_to_rm and not j_to_rm:
                break
            B_copy = [(i, j) for (i, j) in B_copy if i not in i_to_rm
                                                 and j not in j_to_rm]

        # 7:
        plus_pairs = []
        minus_pairs = []
        plus_pairs.append(B_copy.pop())  # bc the new basis pair is the
                                         # last in B (see #5) and is
                                         # still in B_copy
        while B_copy:
            if len(plus_pairs) > len(minus_pairs):
                for index, (i, j) in enumerate(B_copy):
                    if plus_pairs[-1][0] == i or plus_pairs[-1][1] == j:
                        minus_pairs.append(B_copy.pop(index))
                        break
            else:
                for index, (i, j) in enumerate(B_copy):
                    if minus_pairs[-1][0] == i or minus_pairs[-1][1] == j:
                        plus_pairs.append(B_copy.pop(index))
                        break

        theta = min([X[i][j] for (i, j) in minus_pairs])
        for (i, j) in plus_pairs:
            X[i][j] += theta
        for (i, j) in minus_pairs:
            X[i][j] -= theta

        # 8:
        for (i, j) in minus_pairs:
            if X[i][j] == 0:
                B.remove((i, j))
                break


    # the 'I give up' result:
    return False, None
