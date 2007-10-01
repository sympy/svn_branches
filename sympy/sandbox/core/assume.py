
from basic import Basic, sympify

class Condition(tuple):

    def __repr__(self):
        return '%s(%s)' % (self.__class__.__name__, ', '.join([repr(c) for c in self]))


class Greater(Condition):
    """ Represents condition 'is greater than <rhs>'.
    """

    def __new__(cls, rhs):
        return tuple.__new__(cls, (sympify(rhs),))

    @property
    def rhs(self):
        return self[0]

    def __str__(self):
        return '> ' + str(self.rhs)

    def as_interval(self):
        return Basic.Interval(self.rhs, Basic.oo)
    
class Assume(tuple):

    def __new__(cls, lhs, condition):
        return tuple.__new__(cls, (sympify(lhs), condition))

    @property
    def lhs(self):
        return self[0]

    @property
    def condition(self):
        return self[1]

    def __str__(self):
        return '%s %s' % (self.lhs, self.condition)

class Assumptions(tuple):

    def __new__(cls, *args):
        return tuple.__new__(cls, args)

    def check_positive(self, expr):
        for assume in self:
            if assume.lhs==expr:
                if assume.condition.rhs.is_positive:
                    return True

Basic.Assumptions = Assumptions
