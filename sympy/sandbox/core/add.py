
from utils import memoizer_immutable_args
from basic import Basic, MutableCompositeDict, sympify
from methods import ArithMeths, ImmutableMeths, RelationalMeths

class MutableAdd(ArithMeths, RelationalMeths, MutableCompositeDict):
    """ Represents a sum.

    3 + a + 2*b is Add({1:3, a:1, b:2})

    MutableAdd returns a mutable object. To make it immutable, call
    canonical() method.

    MutableAdd is useful in computing sums efficiently. For example,
    iteration like

      s = Integer(0)
      x = Symbol('x')
      i = 1000
      while i:
        i -= 1
        s += x**i

    can be made about 20 times faster by using

      s = MutableAdd()
      x = Symbol('x')
      i = 1000
      while i:
        i -= 1
        s += x**i
      s = s.canonical()

    See MutableCompositeDict.__doc__ for how to deal with mutable
    instances.
    """

    precedence = Basic.Add_precedence

    # canonize methods

    def update(self, a, p=1):
        """
        Add({}).update(a,p) -> Add({a:p})
        """
        if a.__class__ is dict:
            # construct Add instance from a canonical dictionary
            # it must contain Basic instances as keys as well as values.
            assert len(self)==0,`len(self)` # make sure no data is overwritten
            super(MutableAdd, self).update(a)
            return
        a = Basic.sympify(a)
        if a.is_Number:
            p = a * p
            a = Basic.one
        elif a.is_MutableAdd:
            # (3*x) + ((2*x)*4) -> (3*x) + (8*x)
            # Add({x:3}).update(Add({x:2}), 4) -> Add({x:3}).update(x,2*4)
            for k,v in a.items():
                self.update(k, v * p)
            return
        try:
            self[a] += p
        except KeyError:
            self[a] = sympify(p)
        return

    def canonical(self):
        # self will be modified in-place,
        # always return an immutable object
        for k,v in self.items():
            if v.is_zero:
                # todo: check that a is not NaN, Infinity
                # Add({a:0}) -> 0
                del self[k]
        # turn self to an immutable instance
        self.__class__ = Add
        if len(self)==0:
            return Basic.zero
        if len(self)==1:
            k,v = self.items()[0]
            if k.is_one:
                # Add({1:3}) -> 3
                return v
            if v.is_one:
                # Add({a:1}) -> a
                return k
        return self

    # arithmetics methods
    def __iadd__(self, other):
        self.update(other)
        return self


class Add(ImmutableMeths, MutableAdd):
    """ Represents a sum.

    Add returns an immutable object. See MutableAdd for
    a more efficient way to compute sums.
    """

    # constructor methods
    @memoizer_immutable_args("Add.__new__")
    def __new__(cls, *args, **options):
        return MutableAdd(*args, **options).canonical()

    # canonize methods
    def canonical(self):
        return self

    # arithmetics methods
    def __iadd__(self, other):
        return Add(self, other)

    # object identity methods
    def __hash__(self):
        try:
            return self.__dict__['_cached_hash']
        except KeyError:
            h = self._cached_hash = sum(map(hash, self.items()))
        return h

    def split(self, op, *args, **kwargs):
        if op == "+" and len(self) > 1:
            return sorted([c*x for x, c in self.items()])
        if op == "*" and len(self) == 1:
            x, c = self.items()[0]
            return [c] + x.split(op, *args, **kwargs)
        if op == "**":
            return [self, Basic.Number(1)]
        return [self]

    def tostr(self, level=0):
        seq = []
        items = sorted(self.items())
        p = self.precedence
        for term, coef in items:
            if coef > 0:
                if seq: seq.append(" + ")
            else:
                if seq: seq.append(" - ")
                else:   seq.append("-")
                coef = -coef
            if term == 1:
                seq.append(coef.tostr(p))
            elif coef.is_Integer and coef == 1:
                seq.append(term.tostr(p))
            elif coef.is_Fraction:
                seq.append("(" + coef.tostr() + ")" + "*" + term.tostr(p))
            else:
                seq.append(coef.tostr(p) + "*" + term.tostr(p))
        r = "".join(seq)
        if p<=level:
            return '(%s)' % r
        return r
