
import types
from utils import dualmethod, dualproperty
from basic import Atom, Composite, Basic, BasicType, sympify
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

    def __new__(typ, *args, **kws):
        if isinstance(args[0], type):
            # create a class of undefined function
            if len(args)==2:
                ftype, name = args
                attrdict = ftype.__dict__.copy()
            else:
                ftype, name, signature = args
                attrdict = ftype.__dict__.copy()
                attrdict['signature'] = signature
            assert ftype is UndefinedFunction,`ftype`
            bases = (ftype,)
            #typ.set_methods_as_dual(name, attrdict)
            func = type.__new__(typ, name, bases, attrdict)
        else:
            # defined functions
            name, bases, attrdict = args

            attrdict['is_undefined_Function'] = False
            
            attrdict['is_'+name] = dualproperty(lambda self:True)
            setattr(Basic, 'is_' + name,
                    property(lambda self:False,
                             lambda cls:isinstance(cls, getattr(Basic, name))))
            
            func = type.__new__(typ, name, bases, attrdict)

            typ._set_methods_as_dual(func, attrdict)

            # predefined objest is used by parser
            Basic.predefined_objects[name] = func

            # set Basic.Class attributes:
            setattr(Basic, func.__name__, func)
            
        return func

    @classmethod
    def _set_methods_as_dual(cls, func, attrdict):
        name = func.__name__
        methods = []
        names = []
        for n in attrdict.keys():
            if n in ['__new__', '__init__']:
                continue
            mth = attrdict[n]
            if isinstance(mth, types.FunctionType) and cls.__dict__.has_key(n):
                methods.append((n, mth))
                names.append(n)
        for c in func.__bases__:
            for n in getattr(c,'_dualmethod_names',[]):
                if n not in names:
                    mth = getattr(c, n)
                    methods.append((n, mth))
                    names.append(n)
        for (n,mth) in methods:
            # being verbose for a while:
            print 'applying dualmethod to %s.%s' % (name, n)
            setattr(func, n, dualmethod(mth))
        func._dualmethod_names = names
        return

    def torepr(cls):
        if cls.is_undefined_Function:
            for b in cls.__bases__:
                if b.__name__.endswith('Function'):
                    return "%s('%s')" % (b.__name__, cls.__name__)
            return "Function('%s')" % (cls.__name__)
        return type.__repr__(cls)

    def tostr(cls, level=0):
        return cls.__name__

    def get_precedence(cls):
        return Basic.Atom_precedence

    @property
    def precedence(cls):
        return Basic.Atom_precedence

    #precedence = Basic.Atom_precedence

    def try_power(cls, exponent):
        return

    def split(cls, op, *args, **kwargs):
        return [cls]

    def fdiff(cls, index=0):
        raise NotImplementedError('%s.fdiff' % (cls.__name__))

    def atoms(cls, type=None):
        if type is not None and not isinstance(type, (object.__class__, tuple)):
            type = Basic.sympify(type).__class__
        if type is None or isinstance(cls, type):
            return set([cls])
        return set()

Basic.FunctionClass = FunctionClass

class Function(ArithMeths, Composite, tuple):
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
                cls = UndefinedFunction
            return FunctionClass(cls, *args)
        args = map(sympify, args)
        cls.signature.validate(args)
        r = cls.canonize(args, **options)
        if isinstance(r, Basic):
            return r
        elif r is None:
            pass
        elif not isinstance(r, tuple):
            args = (r,)
        # else we have multiple valued function
        return tuple.__new__(cls, args)

    def __hash__(self):
        try:
            return self.__dict__['_cached_hash']
        except KeyError:
            h = hash((self.__class__.__class__, tuple(self)))
            self._cached_hash = h
        return h

    def __eq__(self, other):
        other = sympify(other)
        if other is self: return True
        if not other.is_Function: return False
        if not (other.__class__.__name__==self.__class__.__name__): return False
        return tuple.__eq__(self, other)

    @property
    def args(self):
        return tuple(self)

    @property
    def func(self):
        return self.__class__
        
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

    @dualproperty
    def precedence(cls):
        return Basic.Apply_precedence

    def subs(self, old, new):
        old = sympify(old)
        new = sympify(new)
        if self==old:
            return new
        func = self.__class__
        flag = False
        if func==old:
            func = new
        if func is not self.__class__:
            flag = True
        args = []
        for a in self.args:
            new_a = a.subs(old, new)
            if new_a==a:
                new_a = a
            if new_a is not a:
                flag = True
            args.append(new_a)
        if flag:
            return func(*args)
        return self

    def split(cls, op, *args, **kwargs):
        return [cls]

    def try_power(cls, exponent):
        return

    def atoms(self, type=None):
        return Basic.atoms(self, type).union(self.__class__.atoms(type))

    def __call__(self, *args):
        """
        (f(g))(x) -> f(g(x))
        (f(g1,g2))(x) -> f(g1(x), g2(x))
        """
        return self.__class__(*[a(*args) for a in self.args])

class UndefinedFunction(Function):

    signature = FunctionSignature(None, (Basic,))

class SingleValuedFunction(Function):
    """
    Single-valued functions.
    """
    signature = FunctionSignature(None, (Basic,))

    def try_derivative(self, s):
        i = 0
        l = []
        r = Basic.zero
        args = self.args
        for a in args:
            i += 1
            da = a.diff(s)
            if da.is_zero:
                continue
            df = self.func.fdiff(i)
            l.append(df(*args) * da)
        return Basic.Add(*l)

class Lambda(FunctionClass):

    def __new__(cls, arguments, expression):
        if not isinstance(arguments, (tuple,list)):
            arguments = [sympify(arguments)]
        else:
            arguments = map(sympify, arguments)
        expr = sympify(expression)
        if expr.is_Function and tuple(arguments)==expr.args:
            return expr.__class__
        args = []
        for a in arguments:
            d = a.as_dummy()
            expr = expr.subs(a, d)
            args.append(d)
        args = tuple(args)
        name = 'Lambda(%s, %s)' % (args, expr)
        bases = (LambdaFunction,)
        attrdict = LambdaFunction.__dict__.copy()
        attrdict['_args'] = args
        attrdict['_expr'] = expr
        attrdict['nofargs'] = len(args)
        func = type.__new__(cls, name, bases, attrdict)        
        return func

    def __init__(cls,*args):
        pass

class LambdaFunction(Function):
    """ Defines Lambda function properties.
    
    LambdaFunction instance will never be created.
    """

    def __new__(cls, *args):
        n = cls.nofargs
        if n!=len(args):
            raise TypeError('%s takes exactly %s arguments (got %s)'\
                            % (cls, n, len(args)))
        expr = cls._expr
        for d,a in zip(cls._args, args):
            expr = expr.subs(d,sympify(a))
        return expr
