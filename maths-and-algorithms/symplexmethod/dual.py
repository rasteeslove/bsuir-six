"""
Двойственный симплекс-метод.
"""

import copy
import numpy as np

from symplexmethod import utils


# the max number of iterations to attempt:
MAX_ITER = 42


def iteration(c, A, b, B, Ab_inv_prev, index):
    """
    Итерация двойственного симплекс-метода.

    INPUT:
    - c
    - A
    - b
    - B
    - Ab_inv_prev: матрица обратная матрице Ab из предыдущей итерации
      (на первой итерации - None)
    - index: the index of the element of the B vector that got changed
      in the previous iteration

    OUTPUT: (iteration bundle tuple)
    - solved: bool
    - infeasible: bool
    - kappa
    - y
    - Ab_inv: Ab_inv calculated in this iteration
    - index: index calculated in this iteration

    All changes to the input variables are made by reference.
    """
    n = len(c)

    nB = utils.list_diff(B, list(range(n)))
    Ab = A[:, B]

    if Ab_inv_prev is None and index is None:
        Ab_inv = np.linalg.inv(Ab)
    else:
        Ab_inv = utils.smart_invertion(Ab_inv_prev, Ab[:, index], index)

    cb = [c[i] for i in B]
    y = cb @ Ab_inv
    kappa = np.zeros(n)
    kappa_B = Ab_inv @ b
    for Bi, kappa_Bi in zip(B, kappa_B):
        kappa[Bi] = kappa_Bi

    if all([el >= 0 for el in kappa]):
        return True, False, kappa, y, None, None

    for i, el in enumerate(kappa):
        if el < 0:
            kappa_ast_index = i
            break

    for i, el in enumerate(B):
        if el == kappa_ast_index:
            kappa_ast_index_B_index = i # oh boy
            break

    delta_y = Ab_inv[kappa_ast_index_B_index]
    
    mu = {}
    for j in nB:
        mu[j] = delta_y @ A[:, j]

    if all([el >= 0 for el in list(mu.values())]):
        return True, True, kappa, y, None, None

    sigma = {}
    for i in nB:
        sigma[i] = (c[i] - A[:,i]@y) / mu[i]

    sigma0_index = nB[0]
    for i, s in sigma.items():
        if s < sigma[sigma0_index]:
            sigma0_index = i
            break

    for i, Bi in enumerate(B):
        if Bi == kappa_ast_index:
            B[i] = sigma0_index
            new_index = i
            break
    
    return False, False, None, None, Ab_inv, new_index


def run(c, A, b, B):
    """
    Алгоритм двойственного симплекс-метода.

    INPUT:
    - c
    - A
    - b
    - B

    OUTPUT: (dual symplex method bundle dict)
    - iter_num: number of iterations made
    - infeasible: True if the LPP is found to be infeasible
    - solved: True, если решение ЗЛП найдено
    - kappa: оптимальный план для прямой ЗЛП
    - y: оптимальный план для двойственной ЗЛП
    - B: итоговое множество базисных индексов
    """

    c = copy.deepcopy(c)
    A = copy.deepcopy(A)
    b = copy.deepcopy(b)
    B = copy.deepcopy(B)

    Ab_inv = None
    index = None
    for i in range(MAX_ITER):
        (solved, infeasible, kappa, y,
            Ab_inv, index) = iteration(c, A, b, B, Ab_inv, index)
        if infeasible:
            return {
                'iter_num': i+1,
                'infeasible': True,
                'solved': True,
            }
        if solved:
            return {
                'iter_num': i+1,
                'infeasible': False,
                'solved': True,
                'kappa': kappa,
                'y': y,
                'B': B,
            }

    # the "I give up" result
    return {
        'iter_num': i+1,
        'infeasible': False,
        'solved': False,
        'kappa': kappa,
        'y': y,
        'B': B,
    }
