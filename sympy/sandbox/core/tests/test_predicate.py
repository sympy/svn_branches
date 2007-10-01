
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
