"""
Some additional functions for the symplex method.
"""

import copy
import numpy as np


def list_diff(a, b):
    """
    Get 2 lists difference (as if they are sets)
    """
    return list(set(a) - set(b)) + list(set(b) - set(a))


def replace_col(A, b, index):
    """
    Replace A matrix column #index by the b vector.
    """
    assert len(A) == len(b)
    n = len(A)
    m = len(A[0])
    for i in range(n):
        assert len(A[i]) == m
        A[i][index] = b[i]


def smart_invertion(A_inv, x, i):
    """
    Get A matrix inverted, x vector and i index.
    Return A dash matrix inverted, or None if not invertable.
    """
    n = len(A_inv)

    # 1:
    l = A_inv @ x
    if l[i] == 0:
        return None

    # 2:
    l_wave = copy.deepcopy(l)
    l_wave[i] = -1

    # 3:
    l_hat = -(1/l[i]) * l_wave

    # 4:
    Q = np.identity(n)
    replace_col(Q, l_hat, i)

    # 5:
    A_dash_inv = optimul(Q, A_inv, i)
    return A_dash_inv


def optimul(A, B, index):
    # TODO: some checks and assertions should be here

    n = len(A)

    C = np.zeros([n, n])
    for i in range(n):
        for j in range(n):
            C[i][j] += A[i][index] * B[index][j]
            if i != index:
                C[i][j] += B[i][j]

    return C
