
from parser import Expr
from utils import memoizer_immutable_args

ordering_of_classes = [
    'int','long',
    
    'ImaginaryUnit','Infinity','ComplexInfinity','NaN','Exp1','Pi',
    'Integer','Fraction','Real','Interval',
    'Symbol',
    'MutableMul', 'Mul', 'MutableAdd', 'Add',
    'FunctionClass',
    'Function',
    'sin','cos',
    'Equality','Unequality','StrictInequality','Inequality',
    ]

class BasicType(type):

    classnamespace = dict()
    def __init__(cls,*args,**kws):
        if not cls.undefined_Function:
            # make Basic subclasses available as attributes
            # set is_<classname> = True and False for other classes
            n = cls.__name__
            c = BasicType.classnamespace.get(n)
            if c is None:
                setattr(cls, 'is_' + n, True)
                for k, v in BasicType.classnamespace.items():
                    setattr(v, 'is_' + n, False)
                BasicType.classnamespace[n] = cls
            else:
                print 'Ignoring redefinition of %s: %s defined earlier than %s' % (n, c, cls)
        type.__init__(cls, *args, **kws)

    def __getattr__(cls, name):
        try: return BasicType.classnamespace[name]
        except KeyError: pass
        raise AttributeError("'%s' object has no attribute '%s'"%
                             (cls.__name__, name))

    def __cmp__(cls, other):
        if cls is other: return 0
        if not isinstance(other, type):
            return cmp(cls, other.__class__) or -1            
        n1 = cls.__name__
        n2 = other.__name__
        unknown = len(ordering_of_classes)+1
        try:
            i1 = ordering_of_classes.index(n1)
        except ValueError:
            if not cls.undefined_Function:
                print 'ordering_of_classes is missing',n1,cls
            i1 = unknown
        try:
            i2 = ordering_of_classes.index(n2)
        except ValueError:
            if not other.undefined_Function:
                print 'ordering_of_classes is missing',n2,other
            i2 = unknown
        if i1 == unknown and i2 == unknown:
            return cmp(n1, n2)
        return cmp(i1,i2)


class Basic(object):

    __metaclass__ = BasicType
    undefined_Function = False

    Lambda_precedence = 1
    Add_precedence = 40
    Mul_precedence = 50
    Pow_precedence = 60
    Apply_precedence = 70
    Item_precedence = 75
    Atom_precedence = 1000

    @staticmethod
    def sympify(a, sympify_lists=False):
        """Converts an arbitrary expression to a type that can be used
           inside sympy. For example, it will convert python int's into
           instance of sympy.Integer, floats into intances of sympy.Float,
           etc. It is also able to coerce symbolic expressions which does
           inherit after Basic. This can be useful in cooperation with SAGE.

           It currently accepts as arguments:
               - any object defined in sympy (except maybe matrices [TODO])
               - standard numeric python types: int, long, float, Decimal
               - strings (like "0.09" or "2e-19")

           If sympify_lists is set to True then sympify will also accept
           lists, tuples and sets. It will return the same type but with
           all of the entries sympified.

           If the argument is already a type that sympy understands, it will do
           nothing but return that value. This can be used at the begining of a
           function to ensure you are working with the correct type.

           >>> from sympy import *

           >>> sympify(2).is_integer
           True
           >>> sympify(2).is_real
           True

           >>> sympify(2.0).is_real
           True
           >>> sympify("2.0").is_real
           True
           >>> sympify("2e-45").is_real
           True

        """

        if isinstance(a, Basic):
            return a
        if isinstance(a, bool):
            raise NotImplementedError("bool support")
        if isinstance(a, (int, long)):
            return Basic.Integer(a)
        if isinstance(a, float):
            return Basic.Float(a)
        if isinstance(a, complex):
            real, imag = map(Basic.sympify, (a.real, a.imag))
            ireal, iimag = int(real), int(imag)
            if ireal + iimag*1j == a:
                return ireal + iimag*Basic.I
            return real + Basic.I * imag
        if isinstance(a, (list, tuple)) and len(a) == 2:
            return Basic.Interval(*a)
        if isinstance(a, (list,tuple,set)) and sympify_lists:
            return type(a)([Basic.sympify(x, True) for x in a])
        if not isinstance(a, str):
            # At this point we were given an arbitrary expression
            # which does not inherit after Basic. This may be
            # SAGE's expression (or something alike) so take
            # its normal form via str() and try to parse it.
            a = str(a)
        try:
            return Expr(a).tosymbolic()
        except Exception, msg:
            raise ValueError("%s is NOT a valid SymPy expression: %s" % (`a`, msg))

    predefined_objects = {} # used by parser.

    repr_level = 1

    def __repr__(self):
        if Basic.repr_level == 0:
            return self.torepr()
        if Basic.repr_level == 1:
            return self.tostr()
        raise ValueError, "bad value for Basic.repr_level"

    def __str__(self):
        return self.tostr()

    def tostr(self, level=0):
        return self.torepr()

    def compare(self, other):
        """
        Return -1,0,1 if the object is smaller, equal, or greater than other
        (not always in mathematical sense).
        If the object is of different type from other then their classes
        are ordered according to sorted_classes list.
        """
        # all redefinitions of compare method should start with the
        # following three lines:
        if self is other: return 0
        c = cmp(self.__class__, other.__class__)
        if c: return c
        return cmp(id(self), id(other))

    def __nonzero__(self):
        # prevent using constructs like:
        #   a = Symbol('a')
        #   if a: ..
        raise AssertionError("only Relational and Number classes can define __nonzero__ method, %r" % (self.__class__))

    def get_precedence(self):
        raise NotImplementedError('%s.get_precedence()' % (self.__class__.__name__))

    def subs(self, old, new):
        old = sympify(old)
        new = sympify(new)
        if self==old:
            return new
        return self

class Atom(Basic):

    canonical = evalf = lambda self: self

    def torepr(self):
        return '%s()' % (self.__class__.__name__)

    def get_precedence(self):
        return Basic.Atom_precedence

class Composite(Basic):

    def torepr(self):
        return '%s(%s)' % (self.__class__.__name__,', '.join(map(repr, self)))

class MutableCompositeDict(Composite, dict):
    """ Base class for MutableAdd, MutableMul, Add, Mul.

    Notes:

    - In the following comments `Cls` represents `Add` or `Mul`.

    - MutableCls instances may be uncanonical, e.g.

        MutableMul(0,x) -> 0*x
        MutableMul() -> .
    
      The purpose of this is to be able to create an empty instance
      that can be filled up with update method. When done then one can
      return a canonical and immutable instance by calling
      .canonical() method.

    - Cls instances are cached only when they are created via Cls
      classes.  MutableCls instances are not cached.  Nor are cached
      their instances that are turned to immutable objects via the
      note below.

    - <MutableCls instance>.canonical() returns always an immutable
      object, MutableCls instance is turned into immutable object by
      the following code:

        <MutableCls instance>.__class__ = Cls

    - One should NOT do the reverse:

        <Cls instance>.__class__ = MutableCls

    - One cannot use mutable objects as components of some composite
      object, e.g.

        Add(MutableMul(2),3) -> raises TypeError
        Add(MutableMul(2).canonical(),3) -> Integer(5)
    """

    is_immutable = False

    # constructor methods
    def __new__(cls, *args):
        """
        To make MutableClass immutable, execute
          obj.__class__ = Class
        """
        obj = dict.__new__(cls)
        [obj.update(a) for a in args]
        return obj

    def __init__(self, *args):
        # avoid calling default dict.__init__.
        pass

    # representation methods
    def torepr(self):
        return '%s(%s)' % (self.__class__.__name__, dict(self))

    # comparison methods
    def compare(self, other):
        if self is other: return 0
        c = cmp(self.__class__, other.__class__)
        if c: return c
        return dict.__cmp__(self, other)

    @memoizer_immutable_args('MutableCompositeDict.as_tuple')
    def as_tuple(self):
        """
        Use only when self is immutable.
        """
        assert self.is_immutable,\
               '%s.as_tuple() can only be used if instance is immutable' \
               % (self.__class__.__name__)
        return tuple(sorted(self.items()))

    def __getitem__(self, key):
        if self.is_immutable:
            if isinstance(key, slice) or key.__class__ in [int, long]:
                return self.as_tuple()[key]
        return dict.__getitem__(self, key)

    def subs(self, old, new):
        old = sympify(old)
        new = sympify(new)
        if self==old:
            return new
        lst = []
        flag = False
        for (term, coeff) in self[:]:
            new_term = term.subs(old, new)
            if new_term==term:
                new_term = term
            if new_term is not term:
                flag = True
            lst.append((new_term, coeff))
        if flag:
            cls = getattr(Basic,'Mutable'+self.__class__.__name__)
            r = cls()
            for (term, coeff) in lst:
                r.update(term, coeff)
            return r.canonical()
        return self

sympify = Basic.sympify
Expr.register_handler(Basic)
