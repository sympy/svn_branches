
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

def test_operators():
    a,b,c,d = map(Boolean,'abcd')
    assert (~a) & b & (~c) & d == ~a & b & ~c & d

def test_minimize1():
    a,b,c,d = map(Boolean,'abcd')
    f = ~a & b & ~c & ~d | a & ~b & ~c & ~d | a & ~b & c & ~d | a & ~b & c & d
    f = f | a & b & ~c & ~d | a & b & c & d
    f = f | a & ~b & ~c & d | a & b & c & ~d
    atoms, table = f.truth_table()
    fmin = f.minimize()
    table_min = fmin.truth_table(atoms)[1]
    assert table==table_min
    f1,f2 = a & c | b & ~c & ~d | a & ~b,a & c | b & ~c & ~d | a & ~d
    assert fmin in [f1,f2]

def test_minimize2():
    a,b,c,d = Less('x',2),Less('y',1),Equal('x','y+1'),Boolean('a')
    f = ~a & b & ~c & ~d | a & ~b & ~c & ~d | a & ~b & c & ~d | a & ~b & c & d
    f = f | a & b & ~c & ~d | a & b & c & d
    f = f | a & ~b & ~c & d | a & b & c & ~d
    atoms, table = f.truth_table()
    fmin = f.minimize()
    table_min = fmin.truth_table(atoms)[1]
    assert table==table_min
    f1,f2 = a & c | b & ~c & ~d | a & ~b,\
            a & c | b & ~c & ~d | a & ~d
    assert fmin in [f1,f2]

def test_bug1():
    x = Symbol('x')
    r1 = And(IsInteger(x), IsReal(x)).test(IsInteger(x))
    r2 = And(IsInteger(x), IsReal(x)).refine().test(IsInteger(x))
    assert r1==r2

def test_test():
    x = Symbol('x')
    a = IsInteger(x)
    assert a.test(IsInteger(x))==True
    assert a.test(IsFraction(x))==False
    assert a.test(IsRational(x))==True
    assert a.test(IsReal(x))==True
    assert a.test(IsImaginary(x))==False
    assert a.test(IsComplex(x))==True
    assert a.test(IsEven(x))==IsEven(x)
    assert a.test(IsPrime(x))==IsPrime(x)
    assert a.test(And(IsPrime(x),IsEven(x)))==And(IsPrime(x),IsEven(x))


    a = IsEven(x)
    assert a.test(IsInteger(x))==True
    assert a.test(IsFraction(x))==False
    assert a.test(IsRational(x))==True
    assert a.test(IsReal(x))==True
    assert a.test(IsImaginary(x))==False
    assert a.test(IsComplex(x))==True
    assert a.test(IsEven(x))==True
    assert a.test(IsOdd(x))==False
    assert a.test(IsPrime(x))==IsPrime(x)



def test_test_logic():
    a = Boolean('a')
    b = Boolean('b')
    assert a.test(a)==True
    assert Not(a).test(a)==False

    assert a.test(b)==b
    assert Not(a).test(b)==b
    assert a.test(Not(b))==Not(b)
    
    assert Or(a,b).test(a)==True
    assert Or(~a,b).test(a)==b
    assert And(a,b).test(a)==b
    assert And(~a,b).test(a)==False

def test_bug2():
    x = Symbol('x')
    a = IsEven(x)
    assert a.test(IsPrime(x))==IsPrime(x)

def test_signed():
    x = Symbol('x')
    a = IsPositive(x)
    assert a.test(IsPositive(x))==True
    assert a.test(IsNonPositive(x))==False
    assert a.test(IsNegative(x))==False
    assert a.test(IsNonNegative(x))==True

    a = IsNonPositive(x)
    assert a.test(IsPositive(x))==False
    assert a.test(IsNonPositive(x))==True
    #assert a.test(And(a,Not(IsZero(x))))==Not(IsZero(x))
    #assert a.test(IsNonNegative(x))==IsZero(x)
