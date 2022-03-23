"""
The initial phase of the custom 2-phase symplex method of solving LPPs.
"""

import numpy as np
from symplexmethod import main
from symplexmethod import utils


def correcting_algorithm(c_wave, A, b, A_wave, B):
    """
    Корректирующий алгоритм.

    # TODO: возможно стоит добавить лимит на количество итераций

    INPUT:
    - c_wave
    - A
    - b
    - A_wave
    - B

    OUTPUT: (correcting algorithm bundle tuple)
    - A
    - b
    - B
    """
    m = len(A_wave)
    n = len(A_wave[0]) - m

    while True:
        # если в B есть такой индекс jk, что jk > n, ...
        found_jk = False
        for k, jk in enumerate(B):
            if jk >= n:
                found_jk = True
                break
        
        if not found_jk:
            break

        # ... то для каждого небазисного индекса j < n вычислить
        # вектор l[j] = A_wave_b_inv @ A_wave_j
        i = jk - n
        nB = utils.list_diff(B, list(range(n)))
        A_wave_b_inv = np.linalg.inv(A_wave[:, B])
        l = [None]*n
        for j in nB:
            if j < n:
                A_wave_j = A_wave[:, j]
                l[j] = A_wave_b_inv @ A_wave_j

        # 2 случая:
        # 1: пусть найдется индекс j (небазисный) родной переменной,
        #    такой, что k-ая компонента его вектора l не равна нулю:
        found_j = False
        for j, lj in enumerate(l):
            if lj is not None:
                if lj[k] != 0:
                    found_j = True
                    B[k] = j
                    break

        # 2: пусть такого индекса нет:
        if not found_j:
            # 1: из B удалить jk:
            B = np.delete(B, k)
            # 2: из A&b удалить ограничение #i:
            A = np.delete(A, i, 0)
            b = np.delete(b, i)
            # 3: из A_wave удалить ограничение #i:
            A_wave = np.delete(A_wave, i, 0)
            # 4: из A_wave&c_wave удалить столбец/компоненту #(n+i):
            A_wave = np.delete(A_wave, n+i, 1)
            c_wave = np.delete(c_wave, n+i)

    return A, b, B


def run(c, A, b):
    """
    The algorithm for the initial phase.

    INPUT:
    - c
    - A
    - b

    OUTPUT: (init phase bundle dict)
    - success: True if this stage was successful (rn it indicates
      whether the inner main phase algorithm call was successful
      and yielded the solution to вспомогательная ЗЛП)
    - inconsistent: True if the LPP is found to be inconsistent
    - A: new A
    - b: new b
    - x: начальный базисный допустимый план для входной ЗЛП
    - B: множество базисных индексов
    """
    m = len(A)
    n = len(A[0])

    # 1:
    for i in range(m):
        if b[i] < 0:
            b[i] *= -1
            A[i] = [-a for a in A[i]]

    # 2:
    c_wave = np.array([0]*n + [-1]*m)
    Em = np.identity(m)
    A_wave = np.hstack((A, Em))
    x_hat = np.concatenate((np.zeros(n), b))
    B_hat = [n+i for i in range(m)]

    # 3:
    extra_task_solution_bundle = main.run(c_wave, A_wave, x_hat, B_hat)
    etsb = extra_task_solution_bundle

    # some error handling:
    if not etsb['solved']:
        return {
            'success': False,
        }

    y = etsb['x']
    B = etsb['B']

    if any(y[n:]) != 0:
        return {
            'success': True,
            'inconsistent': True,
        }

    x_ast = y[:n]
    A, b, B = correcting_algorithm(c_wave, A, b, A_wave, B)

    return {
        'success': True,
        'inconsistent': False,
        'A': A,
        'b': b,
        'x': x_ast,
        'B': B,
    }
