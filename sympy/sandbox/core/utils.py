all_caches = {}

class dualmethod(object):
    """dualmethod decorator.
    
    Enable calling a method as a class method or as an instance method
    provided that both metaclass and class define methods with the
    same name.
    """
    # got the idea from http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/523033
    
    def __init__(self, func):
        self.func = func
        self.method_name = func.__name__
        self.class_wrapper_name = '%s.%s(<type>) wrapper' \
                                  % (type.__name__, self.func.__name__)
        self.instance_wrapper_name = '%s.%s(<instance>) wrapper' \
                                     % (type.__name__, self.func.__name__)
        
    def __get__(self, obj, typ=None):
        if obj is None:
            def class_wrapper(*args, **kw):
                return getattr(typ.__class__,
                               self.method_name)(typ, *args, **kw)
            class_wrapper.__name__ = self.class_wrapper_name
            return class_wrapper
        else:
            def instance_wrapper(*args, **kw):
                return self.func(obj, *args, **kw)
            instance_wrapper.__name__ = self.instance_wrapper_name
            return instance_wrapper


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
