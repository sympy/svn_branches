all_caches = {}

class dualmethod(object):
    """dualmethod decorator.
    
    Enable calling a method as a class method or as an instance method
    provided that both metaclass and class define methods with the
    same name.

    Consider the following example:

    class AType(type):
        def foo(cls):
            print 'In AType.foo()'

    class A(object):
        __metaclass__ = AType
        def foo(self):
            print 'In A.foo()'

    The objective is to be able to call foo method both as
    `A.foo()` and `A().foo()`. Using the example above,
    a TypeError is raised when calling `A.foo()`:

    >>> A().foo()
    In A.foo()
    >>> A.foo()
    ...
    <type 'exceptions.TypeError'>: unbound method foo() must be called with A instance as first argument (got nothing instead)

    This issue can be overcome by adding dualmethod decorator to
    A.foo method definition:

    class A(object):
        __metaclass__ = AType
        @dualmethod
        def foo(self):
            print 'In A.foo()'

    And now the example works as expected:

    >>> A().foo()
    In A.foo()
    >>> A.foo()
    In AType.foo()

    """
    # got the idea from http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/523033
    
    def __new__(cls, func):
        obj = getattr(func, '_dualmethod', None)
        if obj is not None:
            return obj
        obj = object.__new__(cls)
        obj.func = func
        obj.method_name = func.__name__
        obj.class_wrapper_name = '%s.%s(<type>) wrapper' \
                                 % (type.__name__, func.__name__)
        obj.instance_wrapper_name = '%s.%s(<instance>) wrapper' \
                                    % (type.__name__, func.__name__)
        return obj
        
    def __get__(self, obj, typ=None):
        if obj is None:
            def class_wrapper(*args, **kw):
                return getattr(typ.__class__,
                               self.method_name)(typ, *args, **kw)
            class_wrapper.__name__ = self.class_wrapper_name
            class_wrapper._dualmethod = self
            return class_wrapper
        else:
            def instance_wrapper(*args, **kw):
                return self.func(obj, *args, **kw)
            instance_wrapper.__name__ = self.instance_wrapper_name
            instance_wrapper._dualmethod = self
            return instance_wrapper

class dualproperty(object):
    """ dualproperty decorator.

class AType(type):
    @property
    def foo(cls):
        return 'AType.foo'

class A(object):
    __metaclass__ = AType
    @dualproperty
    def foo(self):
        return 'A.foo'

A.foo -> 'AType.foo'
A().foo -> 'A.foo'

See also dualmethod.
    """
    def __new__(cls, func, type_callback=None):
        obj = object.__new__(cls)
        obj.func = func
        obj.attr_name = func.__name__
        obj.type_callback = type_callback
        return obj
        
    def __get__(self, obj, typ=None):
        if obj is None:
            if self.type_callback is not None:
                return self.type_callback(typ)
            r = getattr(typ.__base__, self.attr_name)
            return r
        else:
            return self.func(obj)

def memoizer_immutable_args(name):
    def make_memoized(func):
        #return func
        func._cache_it_cache = func_cache_it_cache = {}
        def wrapper(*args):
            try:
                r = func_cache_it_cache.get(args, None)
            except TypeError, msg:
                if 'dict objects are unhashable'==str(msg):
                    return func(*args)
                raise
            if r is None:
                func_cache_it_cache[args] = r = func(*args)
            return r
        all_caches[name] = func_cache_it_cache
        wrapper.__name__ = 'wrapper.%s' % (name)
        return wrapper
    return make_memoized

def memoizer_Symbol_new(func):
    func._cache_it_cache = func_cache_it_cache = {}
    def wrapper(cls, name, dummy=False, **options):
        if dummy:
            return func(cls, name, dummy=dummy, **options)
        r = func_cache_it_cache.get(name, None)
        if r is None:
            func_cache_it_cache[name] = r = func(cls, name, dummy=dummy, **options)
        return r
    all_caches['Symbol.__new__'] = func_cache_it_cache
    wrapper.__name__ = 'wrapper.Symbol.__new__'
    return wrapper

def memoizer_Interval_new(func):
    func._cache_it_cache = func_cache_it_cache = {}
    def wrapper(cls, a, b=None, **options):
        if b is None:
            # to ensure that Interval(a) is Interval(a,a)
            args = (a,a)
        else:
            args = (a,b)
        try:
            return func_cache_it_cache[args]
        except KeyError:
            pass
        func_cache_it_cache[args] = r = func(cls, a, b, **options)
        return r
    all_caches['Interval.__new__'] = func_cache_it_cache
    return wrapper

def memoizer_Float_new(func):
    func._cache_it_cache = func_cache_it_cache = {}
    def wrapper(cls, x=0, prec=None, mode=None, **options):
        if prec is None: prec = cls._prec
        if mode is None: mode = cls._mode
        args = (x, prec, mode)
        try:
            return func_cache_it_cache[args]
        except KeyError:
            pass
        func_cache_it_cache[args] = r = func(cls, *args, **options)
        return r
    all_caches['Float.__new__'] = func_cache_it_cache
    return wrapper

def clear_cache():
    """Clear all cached objects."""
    for cache in all_caches.values():
        cache.clear()
