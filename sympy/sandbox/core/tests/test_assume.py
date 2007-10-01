
from sympy.sandbox import *


def test_simple():
    x = Symbol('x')
    expr = sympify('(x**2)**(1/2)')
    assert expr!=x # make sure that expr is not simplified
    assumptions = (
        Assume(x,Greater(1)),
        )
    r = expr.refine(*assumptions)
    assert r==x

