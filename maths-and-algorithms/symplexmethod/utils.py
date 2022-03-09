"""
Some additional functions for the symplex method.
"""

import numpy as np


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
