
import types
from utils import dualmethod
from basic import Atom, Composite, Basic, BasicType
from methods import ArithMeths

class FunctionSignature:
    """
    Function signature defines valid function arguments
    and its expected return values.

    Examples:

    A function with undefined number of arguments and return values:
    >>> f = Function('f', FunctionSignature(None, None))

    A function with undefined number of arguments and one return value:
    >>> f = Function('f', FunctionSignature(None, (Basic,)))

    A function with 2 arguments and a pair in as a return value,
    the second argument must be Python integer:
    >>> f = Function('f', FunctionSignature((Basic, int), (Basic, Basic)))

    A function with one argument and one return value, the argument
    must be float or int instance:
    >>> f = Function('f', FunctionSignature(((float, int), ), (Basic,)))
    """

    def __init__(self, argument_classes = (Basic,), value_classes = (Basic,)):
        self.argument_classes = argument_classes
        self.value_classes = value_classes
        if argument_classes is None:
            # unspecified number of arguments
            self.nof_arguments = None
        else:
            self.nof_arguments = len(argument_classes)
        if value_classes is None:
            # unspecified number of arguments
            self.nof_values = None
        else:
            self.nof_values = len(value_classes)

    def validate(self, args):
        if self.nof_arguments is not None:
            if self.nof_arguments!=len(args):
                # todo: improve exception messages
                raise TypeError('wrong number of arguments')
            for a,cls in zip(args, self.argument_classes):
                if not isinstance(a, cls):
                    raise TypeError('wrong argument type %r, expected %s' % (a, cls))

    def __repr__(self):
        return '%s(%r, %r)' % (self.__class__.__name__,
                               self.argument_classes,
                               self.value_classes)


Basic.FunctionSignature = FunctionSignature

class FunctionClass(ArithMeths, Atom, BasicType):
    """
    Base class for function classes. FunctionClass is a subclass of type.

    Use Function('<function name>' [ , signature ]) to create
    undefined function classes.

    """

    _new = type.__new__
    precedence = Basic.Atom_precedence

    def __new__(cls, arg1, arg2, arg3=None, **options):
        assert not options,`options`
        if isinstance(arg1, type):
            ftype, name, signature = arg1, arg2, arg3
            assert ftype.__name__.endswith('Function'),`ftype`
            attrdict = ftype.__dict__.copy()
            attrdict['undefined_Function'] = True
            if signature is not None:
                attrdict['signature'] = signature
            bases = (ftype,)
            cls.set_methods_as_dual(name, attrdict)
            func = type.__new__(cls, name, bases, attrdict)
        else:
            name, bases, attrdict = arg1, arg2, arg3
            cls.set_methods_as_dual(name, attrdict)
            func = type.__new__(cls, name, bases, attrdict)
            Basic.predefined_objects[name] = func

        return func

    @classmethod
    def set_methods_as_dual(cls, name, attrdict):
        for k in attrdict.keys():
            if k in ['__new__', '__init__']:
                continue
            mth = attrdict[k]
            if isinstance(mth, types.FunctionType) and hasattr(cls,k):
                # be verbose for a while:
                print 'making',name,'method dual:', mth
                attrdict[k] = dualmethod(mth)

    def torepr(cls):
        if cls.undefined_Function:
            for b in cls.__bases__:
                if b.__name__.endswith('Function'):
                    return "%s('%s')" % (b.__name__, cls.__name__)
            return "Function('%s')" % (cls.__name__)
        return type.__repr__(cls)

    def tostr(cls, level=0):
        return cls.__name__

    def get_precedence(cls):
        return Basic.Atom_precedence


class Function(Composite, tuple):
    """
    Base class for applied functions.
    Constructor of undefined classes.

    If Function class (or its derivative) defines a method that FunctionClass
    also has then this method will be dualmethod, i.e. the method can be
    called as class method as well as an instance method.
    """

    __metaclass__ = FunctionClass
    
    signature = FunctionSignature(None, None)

    def __new__(cls, *args, **options):
        if cls.__name__.endswith('Function'):
            if cls is Function and len(args)==1:
                # Default function signature is of SingleValuedFunction
                # that provides basic arithmetic methods.
                cls = SingleValuedFunction
            return FunctionClass(cls, *args, **options)
        args = map(Basic.sympify, args)
        cls.signature.validate(args)
        r = cls.canonize(args, **options)
        if isinstance(r, Basic): return r
        elif r is None:
            pass
        elif not isinstance(r, tuple):
            args = (r,)
        return tuple.__new__(cls, args)
        
    @classmethod
    def canonize(cls, args, **options):
        return

    def torepr(self):
        return '%s(%s)' % (self.__class__.torepr(),
                           ', '.join([a.torepr() for a in self[:]]))

    def tostr(self, level=0):
        p = self.get_precedence()
        r = '%s(%s)' % (self.__class__.tostr(),
                        ', '.join([a.tostr() for a in self[:]]))
        if level<=p:
            return '(%s)' % (r)
        return r

    def get_precedence(self):
        return Basic.Apply_precedence


class SingleValuedFunction(ArithMeths, Function):
    """
    Single-valued functions.
    """
    signature = FunctionSignature(None, (Basic,))
