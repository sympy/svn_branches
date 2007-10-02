
from basic import Basic, Atom
from symbol import Symbol
from function import Function, FunctionSignature
from qm import qm

class BooleanMeths:

    def __invert__(self): return Not(self)            # ~ operator
    def __or__(self, other): return Or(self, other)   # | operator
    def __xor__(self, other): return XOr(self, other) # ^ operator
    def __and__(self, other): return And(self, other) # & operator
    def __ror__(self, other): return Or(self, other)   # | operator
    def __rxor__(self, other): return XOr(self, other) # ^ operator
    def __rand__(self, other): return And(self, other) # & operator

class Boolean(BooleanMeths, Symbol):
    pass

class Predicate(BooleanMeths, Function):
    """ Base class for predicate functions.
    """
    return_canonize_types = (Basic, bool)

    def __eq__(self, other):
        if isinstance(other, Basic):
            if not other.is_Function: return False
            if self.func==other.func:
                return tuple.__eq__(self, other)
            return False
        if isinstance(other, bool):
            return False
        return self==sympify(other)

    def test(self, condition):
        """ Return
        - True if the condition is True assuming self is True
        - False if the condition contradicts with assumption self is True
        - a condition when the test would be True
        """
        if self==condition:
            return True
        return Implies(condition, self).refine()

    def conditions(self, type=None):
        if type is None: type = Condition
        s = set()
        if isinstance(self, type):
            s.add(self)
        for obj in self:
            if obj.is_Predicate:
                s = s.union(obj.conditions(type=type))
        return s

    def refine(self):
        conditions = self.conditions(IsComplex)
        if not conditions: return self
        expr_map = {}
        for c in conditions:
            e = expr_map.get(c.expr)
            if e is None:
                expr_map[c.expr] = c
                continue
            if isinstance(c, e.__class__):
                expr_map[c.expr] = c
        if not expr_map: return self
        expr = self
        for c in conditions:
            e = expr_map.get(c.expr)
            if e==c: continue
            expr = expr.subs(c, e)
        return expr

    def minimize(self):
        """ Return minimal boolean expression using Quine-McCluskey algorithm.

        See
            http://en.wikipedia.org/wiki/Quine-McCluskey_algorithm
        """
        expressions = list(self.atoms(Boolean).union(self.conditions()))
        n = len(expressions)
        r = range(n-1, -1, -1)
        ones = []
        for i in range(2**n):
            expr = self
            # http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/219300
            bvals =  map(lambda y:bool((i>>y)&1), r)
            for s,b in zip(expressions, bvals):
                expr = expr.subs(s, b)
                if isinstance(expr, bool):
                    break
            if expr is True:
                ones.append(i)
        l = []
        r = range(n)
        for t in qm(ones=ones):
            assert len(t)==n,`t,n`
            p = []
            for c,i in zip(t,r):
                if c=='0': p.append(Not(expressions[i]))
                elif c=='1': p.append(expressions[i])
                else: assert c=='X',`c`
            l.append(And(*p))
        return Or(*l)

    def truth_table(self, expressions=None):
        """ Compute truth table of boolean expression.

        Return (table, expressions) where table is a map
        {<boolean values>: <expression truth value>}
        and expressions is a list conditions and boolean
        symbols.
        """
        if expressions is None:
            expressions = list(self.atoms(Boolean).union(self.conditions()))
        n = len(expressions)
        r = range(n-1, -1, -1)
        table = {}
        for i in range(2**n):
            expr = self
            # http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/219300
            bvals =  tuple(map(lambda y:bool((i>>y)&1), r))
            for s,b in zip(expressions, bvals):
                expr = expr.subs(s, b)
                if isinstance(expr, bool):
                    break
            table[bvals] = expr
        return table, expressions

boolean_classes = (Predicate, Boolean, bool)
Predicate.signature = FunctionSignature(None, boolean_classes)


class And(Predicate):
    """ And(..) predicate.

    a & TRUE -> a
    a & FALSE -> FALSE
    a & (b & c) -> a & b & c
    a & a -> a
    a & ~a -> FALSE
    """

    signature = FunctionSignature(list(boolean_classes), boolean_classes)

    @classmethod
    def canonize(cls, operants):
        new_operants = set()
        flag = False
        for o in operants:
            if isinstance(o, And):
                new_operants = new_operants.union(set(o.args))
                flag = True
            elif isinstance(o, bool):
                if not o: return False
                flag = True
            else:
                n = len(new_operants)
                new_operants.add(o)
                if n==len(new_operants):
                    flag = True
        for o in list(new_operants):
            if Not(o) in new_operants:
                return False
        if not new_operants:
            return True
        if len(new_operants)==1:
            return new_operants.pop()
        if flag:
            return cls(*new_operants)
        return        

    def __eq__(self, other):
        if isinstance(other, Basic):
            if not other.is_Function: return False
            if self.func==other.func and len(self)==len(other):
                return sorted(self)==sorted(other)
            return False
        if isinstance(other, bool):
            return False
        return self==sympify(other)

    def tostr(self, level=0):
        r = '&'. join([c.tostr(self.precedence) for c in self])
        if self.precedence <= level:
            r = '(%s)' % r
        return r

class Or(Predicate):
    """
    a | TRUE -> TRUE
    a | FALSE -> a
    a | (b | c) -> a | b | c
    a | a -> a
    a | ~a -> TRUE
    """
    signature = FunctionSignature(list(boolean_classes), boolean_classes)

    @classmethod
    def canonize(cls, operants):
        new_operants = set()
        flag = False
        for o in operants:
            if isinstance(o, Or):
                new_operants = new_operants.union(set(o.args))
                flag = True
            elif isinstance(o, bool):
                if o: return True
                flag = True
            else:
                n=len(new_operants)
                new_operants.add(o)
                if n==len(new_operants):
                    flag = True
        for o in list(new_operants):
            if Not(o) in new_operants:
                return True
        if not new_operants:
            return False
        if len(new_operants)==1:
            return new_operants.pop()
        if flag:
            return cls(*new_operants)
        return

    def __eq__(self, other):
        if isinstance(other, Basic):
            if not other.is_Function: return False
            if self.func==other.func and len(self)==len(other):
                return sorted(self)==sorted(other)
            return False
        if isinstance(other, bool):
            return False
        return self==sympify(other)

    def tostr(self, level=0):
        r = ' | '. join([c.tostr(self.precedence) for c in self])
        if self.precedence <= level:
            r = '(%s)' % r
        return r

class XOr(Predicate):
    """
    a ^ TRUE -> ~a
    a ^ FALSE -> a
    a ^ (b ^ c) -> a ^ b ^ c
    a ^ a -> FALSE
    a ^ ~a -> TRUE
    """


    signature = FunctionSignature(list(boolean_classes), boolean_classes)

    @classmethod
    def canonize(cls, operants):
        if not operants:
            return False
        if len(operants)==1:
            arg = operants[0]
            return arg
        if False in operants:
            return cls(*[o for o in operants if o is not False])
        new_operants = []        
        flag = False
        truth_index = 0
        for o in operants:
            if isinstance(o, bool):
                flag = True
                if o: truth_index += 1
            elif o.is_XOr:
                flag = True
                new_operants.extend(o.args)
            else:
                new_operants.append(o)
        operants = new_operants
        new_operants = []
        for o in operants:
            if o not in new_operants:
                po = Not(o)
                if po in new_operants:
                    flag = True
                    truth_index += 1
                    new_operants.remove(po)
                else:
                    new_operants.append(o)
            else:
                new_operants.remove(o)
                flag = True
        if flag:
            if truth_index % 2:
                if new_operants:
                    new_operants[-1] = Not(new_operants[-1])
                else:
                    return True
            return cls(*new_operants)
        return

    def __eq__(self, other):
        if isinstance(other, Basic):
            if not other.is_Function: return False
            if self.func==other.func and len(self)==len(other):
                return sorted(self)==sorted(other)
            return False
        if isinstance(other, bool):
            return False
        return self==sympify(other)

class Not(Predicate):

    signature = FunctionSignature((boolean_classes,), boolean_classes)

    @classmethod
    def canonize(cls, (arg,)):
        if isinstance(arg, bool):
            return not arg
        if arg.is_Not:
            return arg.args[0]

    def tostr(self, level=0):
        r = '~%s' % (self.args[0].tostr(self.precedence))
        if self.precedence <= level:
            r = '(%s)' % r
        return r

class Implies(Predicate):
    signature = FunctionSignature((boolean_classes,boolean_classes), boolean_classes)

    @classmethod
    def canonize(cls, (lhs, rhs)):
        return Or(Not(lhs), rhs)

class Equiv(Predicate):
    signature = FunctionSignature((boolean_classes, boolean_classes), boolean_classes)

    @classmethod
    def canonize(cls, (lhs, rhs)):
        return Not(XOr(lhs, rhs))

class Condition(Predicate):
    """ Base class for conditions.
    """

class Equal(Condition):

    signature = FunctionSignature((Basic, Basic), boolean_classes)

    @classmethod
    def canonize(cls, (lhs, rhs)):
        if lhs==rhs: return True
        if lhs.is_Number and rhs.is_Number: return False

    @property
    def lhs(self): return self[0]
    @property
    def rhs(self): return self[1]

    def tostr(self, level=0):
        r = '%s == %s' % (self.lhs.tostr(self.precedence),self.rhs.tostr(self.precedence))
        if self.precedence <= level:
            r = '(%s)' % r
        return r

class Less(Condition):

    signature = FunctionSignature((Basic, Basic), boolean_classes)
    
    @classmethod
    def canonize(cls, (lhs, rhs)):
        if lhs.is_Number and rhs.is_Number:
            return lhs < rhs
        elif lhs==rhs: return False

    @property
    def lhs(self): return self[0]
    @property
    def rhs(self): return self[1]

    def tostr(self, level=0):
        r = '%s < %s' % (self.lhs.tostr(self.precedence),self.rhs.tostr(self.precedence))
        if self.precedence <= level:
            r = '(%s)' % r
        return r

class IsComplex(Condition):

    signature = FunctionSignature((Basic,), boolean_classes)

    @classmethod
    def canonize(cls, (arg,)):
        if arg.is_Real: return True
        if arg.is_ImaginaryUnit: return True

    @property
    def expr(self):
        return self[0]

class IsReal(IsComplex):

    @classmethod
    def canonize(cls, (arg,)):
        if arg.is_Real: return True
        if arg.is_Number: return False
        if arg.is_ImaginaryUnit: return False

class IsRational(IsReal):
    
    @classmethod
    def canonize(cls, (arg,)):
        if arg.is_Rational: return True
        if arg.is_Number: return False
        if arg.is_ImaginaryUnit: return False

class IsIrrational(IsReal):

    @classmethod
    def canonize(cls, (arg,)):
        return And(IsReal(arg), Not(IsRational(arg)))

class IsInteger(IsRational):
    
    @classmethod
    def canonize(cls, (arg,)):
        if arg.is_Integer: return True
        if arg.is_Number: return False
        if arg.is_ImaginaryUnit: return False

class IsFraction(IsRational):
    
    @classmethod
    def canonize(cls, (arg,)):
        return And(IsRational(arg), Not(IsInteger(arg)))

class IsPrime(IsInteger):

    @classmethod
    def canonize(cls, (arg,)):
        # need prime test
        pass

class IsComposite(IsInteger):

    @classmethod
    def canonize(cls, (arg,)):
        return And(IsInteger(arg), Not(IsPrime(arg)))

class IsNonNegative(IsReal):
    
    @classmethod
    def canonize(cls, (arg,)):
        if arg.is_ImaginaryUnit: return False
        return Not(Less(arg, 0))

class IsPositive(IsNonNegative):
    
    @classmethod
    def canonize(cls, (arg,)):
        if arg.is_ImaginaryUnit: return False
        return Less(0, arg)

class IsNonPositive(IsReal):
    
    @classmethod
    def canonize(cls, (arg,)):
        if arg.is_ImaginaryUnit: return False
        return Not(Less(0, arg))

class IsNegative(IsNonPositive):
        
    @classmethod
    def canonize(cls, (arg,)):
        if arg.is_ImaginaryUnit: return False
        return Less(arg, 0)
        
