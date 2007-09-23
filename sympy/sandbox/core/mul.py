
from utils import memoizer_immutable_args
from basic import Basic, MutableCompositeDict, sympify
from methods import ArithMeths, ImmutableMeths, RelationalMeths

class MutableMul(ArithMeths, RelationalMeths, MutableCompositeDict):
    """Mutable base class for Mul. This class is used temporarily
    during construction of Mul objects.

    See MutableCompositeDict.__doc__ for how to deal with mutable
    instances.
    """

    # canonize methods
    
    def update(self, a, p=1):
        """
        Mul({}).update(a,p) -> Mul({a:p})
        """
        if a.__class__ is dict:
            # construct Mul instance from a canonical dictionary,
            # it must contain Basic instances as keys as well as values.
            assert len(self)==0,`len(self)` # make sure no data is overwritten
            assert p is 1,`p`
            super(MutableMul, self).update(a)
            return
        a = Basic.sympify(a)
        if a.is_MutableAdd and len(a)==1:
            # Mul({x:3,4:1}).update(Add({x:2})) -> Mul({x:3+1,4:1,2:1})
            k, v = a.items()[0]
            self.update(k, p)
            self.update(v, p)
            return
        if a.is_MutableMul:
            # Mul({x:3}).update(Mul({x:2}), 4) -> Mul({x:3}).update(x,2*4)
            for k,v in a.items():
                # todo?: make it noncommutative product for (a**2)**(1/2)
                #        (a**z)**w where z,w are complex numbers
                self.update(k, v * p)
            return
        try:
            self[a] += p
        except KeyError:
            self[a] = sympify(p)

    def canonical(self):
        # self will be modified in-place,
        # always return an immutable object
        n = Basic.one
        for k,v in self.items():
            if v==0:
                # Mul({a:0}) -> 1
                del self[k]
                continue
            a = k.try_power(v)
            if a is None: continue
            del self[k]
            if a.is_Number:
                n *= a
            else:
                self.update(a)
                return self.canonical()
        if self.has_key(n):
            self.update(n)
            return self.canonical()
        self.__class__ = Mul
        if len(self)==0:
            return n
        obj = self
        if len(self)==1:
            # Mul({a:1}) -> a
            k,v = self.items()[0]
            if v.is_one:
                obj = k
        if n.is_one:
            return obj
        s = Basic.MutableAdd()
        s.update(obj, n)
        return s.canonical()

    # arithmetics methods
    def __imul__(self, other):
        self.update(other)
        return self


class Mul(ImmutableMeths, MutableMul):
    """Represents a product, with repeated factors collected into
    powers using a dict representation. The product a**m * b**n
    (where m and n may be arbitrary expressions and not just
    integers) is represented as Mul({a:m, b:n}).

    Note that purely rational multiples are counted using the Add
    class, so 3*x*y**2 --> Add({Mul({x:1, y:2}):3}).
    """

    # constructor methods
    @memoizer_immutable_args("Mul.__new__")
    def __new__(cls, *args, **options):
        return MutableMul(*args, **options).canonical()

    # arithmetics methods
    def __imul__(self, other):
        return Mul(self, other)

    # object identity methods
    def __hash__(self):
        try:
            return self.__dict__['_cached_hash']
        except KeyError:
            h = self._cached_hash = sum(map(hash, self.items()))
        return h

    def canonical(self):
        return self

    def split(self, op, *args, **kwargs):
        if op == '*':
            return sorted([x**c for x, c in self.items()])
        if op == '**' and len(self) == 1:
            return list(self.items()[0])
        return [self]

    def tostr(self):
        seq = []
        items = sorted(self.items())
        for base, exp in items:
            basestr = base.tostr()
            if not (base.is_Symbol or (base.is_Integer and base > 0)):
                basestr = "(" + basestr + ")"
            if exp.is_Integer and exp == 1:
                seq.append(basestr)
            else:
                expstr = exp.tostr()
                if not (exp.is_Integer or exp.is_Symbol):
                    expstr = "(" + expstr + ")"
                seq.append(basestr + "**" + expstr)
        return "*".join(seq)


class Pow(Basic):

    def __new__(cls, a, b):
        a = Basic.sympify(a)
        b = Basic.sympify(b)
        if b.is_zero: return Basic.one
        if b.is_one: return a
        if a.is_one: return a
        m = MutableMul()
        m.update(a,b)
        return m.canonical()

def sqrt(x):
    return Pow(x, Basic.Rational(1,2))
