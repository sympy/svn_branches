
from sympy.sandbox import *

def test_truth_table():

    assert Not(False)==True
    assert Not(True)==False
    assert Or(False, False)==False
    assert Or(False, True)==True
    assert Or(True, False)==True
    assert Or(True, True)==True
    assert XOr(False, False)==False
    assert XOr(False, True)==True
    assert XOr(True, False)==True
    assert XOr(True, True)==False
    assert And(False, False)==False
    assert And(False, True)==False
    assert And(True, False)==False
    assert And(True, True)==True
    assert Implies(False, False)==True
    assert Implies(False, True)==True
    assert Implies(True, False)==False
    assert Implies(True, True)==True
    assert Equiv(False, False)==True
    assert Equiv(False, True)==False
    assert Equiv(True, False)==False
    assert Equiv(True, True)==True

def test_trivial():
    assert Or(False)==False
    assert Or(True)==True
    assert And(False)==False
    assert And(True)==True
    assert XOr(False)==False
    assert XOr(True)==True

    # logic: a <op> <nothing> -> a
    assert Or()==False   # a OR False -> a
    assert And()==True  # a AND True -> a
    assert XOr()==False # a XOR False -> a

def test_bug1():
    x = Symbol('x')
    r1 = And(IsInteger(x), IsReal(x)).test(IsInteger(x))
    r2 = And(IsInteger(x), IsReal(x)).refine().test(IsInteger(x))
    assert r1==r2
