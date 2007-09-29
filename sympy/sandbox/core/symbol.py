
from utils import memoizer_immutable_args, memoizer_Symbol_new
from basic import Atom, Basic, sympify
from methods import ArithMeths#, RelationalMeths

class Symbol(ArithMeths, Atom, str):

    """ Represents a symbol.

    Symbol('x', dummy=True) returns a unique Symbol instance.
    """

    _dummy_count = 0
    is_dummy = False

    
    def __new__(cls, name, dummy=False, **options):
        # when changing the Symbol signature then change memoizer_Symbol_new
        # accordingly    
        assert isinstance(name, str), `name`
        if dummy:
            return Dummy(name)
        return str.__new__(cls, name)

    @property
    def name(self): return str.__str__(self)

    def torepr(self):
        return '%s(%r)' % (self.__class__.__name__, self.name)

    def tostr(self, level=0):
        return self.name

    def compare(self, other):
        if self is other: return 0
        c = cmp(self.__class__, other.__class__)
        if c: return c
        return cmp(str(self), str(other))

    def __eq__(self, other):
        if isinstance(other, Basic):
            if other.is_Dummy: return False
        return str.__eq__(self, other)            

    def __call__(self, *args):
        signature = Basic.FunctionSignature((Basic,)*len(args), (Basic,))
        return Basic.UndefinedFunction(self, signature)(*args)

    def as_dummy(self):
        return Dummy(self.name)

    __hash__ = str.__hash__

    def try_derivative(self, s):
        if self==s:
            return Basic.one
        return Basic.zero

    def fdiff(self, index=1):
        return Basic.zero

class Dummy(Symbol):
    """ Dummy Symbol.
    """
    def __new__(cls, name):
        Symbol._dummy_count += 1
        obj = str.__new__(cls, name)
        obj.dummy_index = Symbol._dummy_count        
        return obj

    def torepr(self):
        return '%s(%r)' % (self.__class__.__name__, self.name)

    def tostr(self, level=0):
        return '_' + self.name

    def __eq__(self, other):
        return self is other

class Wild(Dummy):
    """
    Wild() matches any expression but another Wild().
    """

    def __new__(cls, name=None, exclude=None):
        if name is None:
            name = 'W%s' % (Symbol._dummy_count+1)
        obj = Dummy.__new__(cls, name)
        if exclude is None:
            obj.exclude = None
        else:
            obj.exclude = [Basic.sympify(x) for x in exclude]
        return obj

    def matches(pattern, expr, repl_dict={}, evaluate=False):
        for p,v in repl_dict.items():
            if p==pattern:
                if v==expr: return repl_dict
                return None
        if pattern.exclude:
            for x in pattern.exclude:
                if x in expr:
                    return None
        repl_dict = repl_dict.copy()
        repl_dict[pattern] = expr
        return repl_dict

    def tostr(self, level=0):
        return self.name + '_'
