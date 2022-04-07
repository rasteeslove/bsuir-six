"""

"""

import copy
import numpy as np


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


def solve(a, b, C):
    """
    ...

    INPUT:
    - a
    - b
    - C

    OUTPUT:
    """
    assert np.sum(a) == np.sum(b)

    n = len(a)
    m = len(b)


