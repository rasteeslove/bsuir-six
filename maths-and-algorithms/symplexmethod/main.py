"""
Основная фаза симплекс-метода.
"""

import numpy as np


MAX_ITER = 12


def get_basis_and_nonbasis_indexes(x):
    """
    This function is also to take c. But with a trick.
    """
    B = []
    nB = []
    for i, val in enumerate(x):
        if val == 0:
            nB.append(i)
        else:
            B.append(i)
    return B, nB


def iteration(A, x, c):
    """
    Итерация основной фазы симплекс-метода.
    Return iteration bundle:
    - unsolvable: True if unsolvable
    - solved: True if the LPP is solved
    """
    B, nB = get_basis_and_nonbasis_indexes(x)
    Ab = np.delete(A, nB, 1)
    Ab_inv = np.linalg.inv(Ab) # TODO: use optimul
    cb = np.delete(c, nB)
    u = cb @ Ab_inv
    delta = u @ A - c
    nB_delta = [el for i, el in enumerate(delta) if i in nB]

    if all([el >= 0 for el in nB_delta]):
        return False, True

    j0 = 0
    for i, v in enumerate(nB_delta):
        if v >= 0:
            j0 = i
            break

    z = Ab_inv @ A[:, j0]
    theta = np.array([x[j]/z_i if z_i > 0 else np.inf
                      for z_i, j in zip(z, B)])

    theta0 = np.amin(theta)
    if theta0 == np.inf:
        return True, True
    theta0_index = np.where(theta == theta0)[0][0] # np.where returns a tuple hence the indexing

    j_ast = B[theta0_index]
    j_ast_index = np.where(np.array(B) == j_ast)[0][0]

    B[j_ast_index] = j0
    all_indexes = list(range(len(x)))
    nB = [item for item in all_indexes if item not in B]
    for i in nB:
        x[i] = 0
    x[j0] = theta0
    for j_index, j in enumerate(B):
        if j != j0:
            x[j] -= theta0*z[j_index]
    
    return False, False


def run(c, A, b):
    """
    The main phase algorithm of the custom 2-phase symplex method.
    Return main phase bundle:
    - iter_num: number of iterations made
    - unsolvable: True is unsolvable
    - x: the x vector that is the solution, or None
    - solved: True if the LPP is solved
    """
    nB, B = get_basis_and_nonbasis_indexes(c) # there's a little trick
    
    # 1: calculate x as x0 (начальный базисный доп план)
    A_ = np.delete(A, nB, 1)
    x0 = np.linalg.solve(A_, b).tolist()
    
    for i in nB:
        x0.insert(i, 0)
    x = np.array(x0)

    for i in range(MAX_ITER):
        unsolvable, solved = iteration(A, x, c)
        if unsolvable:
            return i+1, True, None, True
        if solved:
            return i+1, False, x, True

    # the 'I give up' result
    return i+1, False, x, False
