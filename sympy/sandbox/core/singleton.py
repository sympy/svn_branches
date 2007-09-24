
from utils import memoizer_immutable_args
from basic import Atom, Basic, sympify
from methods import ArithMeths, RelationalMeths

class NumberSymbol(ArithMeths, RelationalMeths, Atom):

    @memoizer_immutable_args('NumberSymbol.__new__')
    def __new__(cls):
        return object.__new__(cls)

class ImaginaryUnit(ArithMeths, RelationalMeths, Atom):

    @memoizer_immutable_args('ImaginaryUnit.__new__')
    def __new__(cls):
        return object.__new__(cls)

    def tostr(self, level=0):
        return 'I'

    def try_power(self, other):
        if other.is_Integer:
            if other.is_one:
                # nothing to evaluate
                return
            e = other.p % 4
            if e==0: return Basic.one
            if e==1: return Basic.I
            if e==2: return -Basic.one
            return -Basic.I
        return

I = ImaginaryUnit()
Basic.I = I


class Exp1(NumberSymbol):

    def tostr(self, level=0):
        return 'E'


class Pi(NumberSymbol):

    def tostr(self, level=0):
        return "pi"

pi = Pi()

class GoldenRatio(NumberSymbol):

    pass

class EulerGamma(NumberSymbol):

    pass

class Catalan(NumberSymbol):

    pass

class NaN(NumberSymbol):

    def tostr(self, level=0):
        return 'nan'

    def try_power(self, other):
        if other.is_zero:
            return Basic.one
        return self

class Infinity(NumberSymbol):

    def tostr(self, level=0):
        return 'oo'

    def try_power(self, other):
        if other.is_NaN:
            return other
        if other.is_Number:
            if other.is_zero:
                return Basic.one
            if other.is_one:
                return
            if other.is_positive:
                return self
            if other.is_negative:
                return Basic.zero
        if other.is_Infinity:
            return self
        if other==-self:
            return Basic.zero

class ComplexInfinity(NumberSymbol):

    def tostr(self, level=0):
        return 'zoo'

    def try_power(self, other):
        if other.is_NaN:
            return other
        if other.is_Number:
            if other.is_zero:
                return Basic.one
            if other.is_positive:
                return self
            if other.is_negative:
                return Basic.zero

nan = NaN()
oo = Infinity()
zoo = ComplexInfinity()
E = Exp1()
Basic.nan = nan
Basic.oo = oo
Basic.zoo = zoo
Basic.E = E
