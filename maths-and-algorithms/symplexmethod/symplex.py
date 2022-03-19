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
    Полный алгоритм для симплекс метода.

    INPUT: ЗЛП в канонической форме:
    - c: вектор стоимостей
    - A: матрица ограничений
    - b

    OUTPUT: symplex method bundle dict:
    - solved: True if the solution is found
    - inconsistent: True if LPP is found to be inconsistent
    - unbound: True если обнаружилось, что ц.ф. ЗЛП не ограничена
      сверху на множестве допустимых планов
    - x: либо оптимальный план ЗЛП, либо None
    - details (optional): примечания
    """
    
    init_phase_bundle = initial.run(c, A, b)

    if not init_phase_bundle['success']:
        return {
            'solved': False,
            'details': 'initial phase failure; '
            'inner main phase algorithm reached iteration number limit'
        }

    # process the initial phase result:
    x = init_phase_bundle['x']
    B = init_phase_bundle['B']

    main_phase_bundle = main.run(c, A, x, B)

    if not main_phase_bundle['solved']:
        return {
            'solved': False,
            'details': 'main phase failure; '
            'main phase algorithm reached iteration number limit'
        }

    # process the main phase result:
    return {
        'solved': True,
        'x': main_phase_bundle['x'],
    }


def scipy_solve(c, A, b):
    """
    Solve an LPP using scipy.
    Return what scipy returns and let the user handle that themself.
    """
    return linprog(-c, A_eq=A, b_eq=b)
