"""
This module contains the means to solve quadratic programming problems.
"""


import copy
from doctest import UnexpectedException
import numpy as np


# the max number of iterations to attempt:
MAX_ITER = 42


def solve(c: np.array, x: np.array, D: np.array,
          A: np.array, b: np.array,
          Jb: list, Jb_ast: list):
    """
    Решение задачи квадратичного программирования.

    INPUT:
    - c
    - x
    - D
    - A
    - b
    - Jb
    - Jb_ast

    OUTPUT:
    - solved
    - unbounded
    - x
    """
    c = copy.deepcopy(c)
    x = copy.deepcopy(x)
    D = copy.deepcopy(D)
    A = copy.deepcopy(A)
    b = copy.deepcopy(b)
    Jb = copy.deepcopy(Jb)
    Jb_ast = copy.deepcopy(Jb_ast)

    for i in range(MAX_ITER):
        # 1:
        Ab = A[:, Jb]
        Ab_inv = np.linalg.inv(Ab)
        c_x = c + x @ D
        u_x = -c_x[Jb] @ Ab_inv
        delta_x = u_x @ A + c_x

        # 2:
        if all([el >= 0 for el in delta_x]):
            return True, False, x

        # 3:
        j0 = 0
        for i, el in enumerate(delta_x):
            if el < 0:
                j0 = i
                break

        # 4:
        l = np.zeros(len(x))
        l[j0] = 1
        Hn = np.hstack((D[Jb_ast][:, Jb_ast], A[:, Jb_ast].T))
        Hs = np.hstack((A[:, Jb_ast], np.zeros((len(A), len(A)))))
        H = np.vstack((Hn, Hs))
        H_inv = np.linalg.inv(H)
        b_ast = np.hstack((D[Jb_ast][:, j0], A[:, j0]))

        x_impostor = -H_inv @ b_ast
        for i in range(len(Jb_ast)):
            l[i] = x_impostor[i]

        # 5:
        theta = {}
        delta = l @ D @ l
        theta[j0] = np.inf if delta == 0 else np.abs(delta_x[j0])/delta
        for j in Jb_ast:
            theta[j] = -x[j]/l[j] if l[j] < 0 else np.inf
        
        j_ast = min(theta, key=theta.get)
        theta0 = theta[j_ast]
        if theta0 == np.inf:
            return True, True, None

        # 6:
        x = x + theta0*l
        if j0 == j_ast:  # 6.1
            Jb_ast.append(j_ast)
        elif j_ast in set(Jb_ast).difference(set(Jb)):  # 6.2
            Jb_ast.remove(j_ast)
        elif j_ast in Jb:
            s = Jb.index(j_ast)
            six_point_three_condition_met = False
            for j_plus in set(Jb_ast).difference(set(Jb)):
                if (Ab_inv @ A[:, j_plus])[s] != 0:  # 6.3
                    six_point_three_condition_met = True
                    Jb = [j if j != j_ast else j_plus for j in Jb]
                    Jb_ast.remove(j_ast)
                    break
            if not six_point_three_condition_met:
                Jb = [j if j != j_ast else j0 for j in Jb]
                Jb_ast = [j if j != j_ast else j0 for j in Jb_ast]
        else:
            raise UnexpectedException('well, thats unexpected innit')

    # the 'I give up' result:
    return False, False, None
