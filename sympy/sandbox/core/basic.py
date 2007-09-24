
ordering_of_classes = [
    'ImaginaryUnit','Infinity','ComplexInfinity','NaN','Exp1',
    'Integer','Fraction','Real','Interval',
    'Symbol',
    'MutableMul', 'Mul', 'MutableAdd', 'Add',
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
        assert isinstance(other,type),`other.__class__`
        n1 = cls.__name__
        n2 = other.__name__
        unknown = len(ordering_of_classes)+1
        try:
            i1 = ordering_of_classes.index(n1)
        except ValueError:
            print 'ordering_of_classes is missing',n1
            i1 = unknown
        try:
            i2 = ordering_of_classes.index(n2)
        except ValueError:
            print 'ordering_of_classes is missing',n2
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
    def sympify(a):
        if isinstance(a, Basic):
            return a
        elif isinstance(a, bool):
            raise NotImplementedError("bool support")
        elif isinstance(a, (int, long)):
            return Basic.Integer(a)
        elif isinstance(a, float):
            return Basic.Float(a)
        raise ValueError("%s is NOT a valid SymPy expression" % `a`)

    repr_level = 1

    def __repr__(self):
        if isinstance(self, type):
            return self.__class__.torepr(self)
        if Basic.repr_level == 0:
            return self.torepr()
        if Basic.repr_level == 1:
            return self.tostr()
        raise ValueError, "bad value for Basic.repr_level"

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


class Atom(Basic):

    canonical = evalf = lambda self: self

    def torepr(self):
        return '%s()' % (self.__class__.__name__)

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

sympify = Basic.sympify
