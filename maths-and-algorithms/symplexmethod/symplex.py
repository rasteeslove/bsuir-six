"""
This is the module whose functionality is to be used from the outside
of the symplexmethod package. It provides the functions to solve LPPs
both using the scipy method, and the custom method implementing the
2-phase algorithm of solving LPPs.
"""

from scipy.optimize import linprog

from symplexmethod import initial
from symplexmethod import main


def custom_solve(c, A, b):
    """
    Input: LPP for which to calculate the optimal plan.
    Output: оптимальный план задачи, если она не ограничена сверху
    на множестве допустимых планов, иначе None.
    """
    
    initial_phase_result = initial.run(c, A, b)

    # process the initial phase result here smh

    iter_num, unsolvable, x, solved = main.run(c, A, b)

    # process the main phase result here smh

    solution = { 'iter_num': iter_num,
                 'unsolvable': unsolvable,
                 'x': x,
                 'solved': solved
               }

    return solution


def scipy_solve(c, A, b):
    """
    Solve an LPP using scipy.
    Return what scipy returns and let the user handle that themself.
    """
    return linprog(-c, A_eq=A, b_eq=b)

