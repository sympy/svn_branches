
from sympy.sandbox import Symbol, sympify, Fraction, sin, Function

def test_parder():
    x = Symbol('x')
    f = Function('f')
    assert sympify('x')==x
    assert sympify('x+1')==1+x
    assert sympify('x*2')==2*x
    assert sympify('x**(3/2)')==x**Fraction(3,2)
    assert sympify('1/2')==Fraction(1,2)
    assert sympify('5/15')==Fraction(1,3)
    assert sympify('x*2')==2*x
    assert sympify('sin(x)')==sin(x)
    #assert sympify('f(x)+sin(x)')==sin(x)+f(x)
    
if __name__ == '__main__':
    test_parser()
