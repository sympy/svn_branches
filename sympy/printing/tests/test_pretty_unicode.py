# -*- coding: utf-8 -*-

from sympy import *
from sympy.printing.pretty import pretty
from sympy.utilities.pytest import XFAIL

x,y = symbols('xy')
th  = Symbol('theta')
ph  = Symbol('phi')

@XFAIL
def upretty(expr):
    return pretty(expr, True)

@XFAIL
def test_upretty_greek():
    assert upretty( oo ) == u'∞'
    assert upretty( Symbol('alpha^+_1') )   ==  u'α⁺₁'

@XFAIL
def test_upretty_funcbraces():
    f = Function('f')
    u = upretty(f(x/(y+1), y))
    s = \
u"""\
 ⎛  x     ⎞
f⎜─────, y⎟
 ⎝1 + y   ⎠\
"""
    assert u == s

@XFAIL
def test_upretty_sqrt():
    u = upretty( sqrt((sqrt(x+1))+1) )
    s = \
u"""\
   ⎽⎽⎽⎽⎽⎽⎽⎽⎽⎽⎽⎽⎽⎽⎽
  ╱       ⎽⎽⎽⎽⎽⎽⎽ 
╲╱  1 + ╲╱ 1 + x  \
"""
    assert u == s

@XFAIL
def test_upretty_integral():
    u = upretty( Integral(sin(th)/cos(ph), (th,0,pi), (ph, 0, 2*pi)) )
    s = \
u"""\
2*π π             
 ⌠  ⌠             
 ⎮  ⎮ sin(θ)      
 ⎮  ⎮ ────── dθ dφ
 ⎮  ⎮ cos(φ)      
 ⌡  ⌡             
 0  0             \
"""
    assert u == s

    u = upretty( Integral(x**2*sin(y), (x,0,1), (y,0,pi)) )
    s = \
u"""\
π 1                
⌠ ⌠                
⎮ ⎮  2             
⎮ ⎮ x *sin(y) dx dy
⌡ ⌡                
0 0                \
"""
    assert u == s
