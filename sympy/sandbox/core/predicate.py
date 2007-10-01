
from basic import Basic, Atom
from symbol import Symbol
from function import Function, FunctionSignature

class Boolean(Symbol):
    pass

class Predicate(Function):
    """ Base class for predicate functions.
    """
    return_canonize_types = (Basic, bool)

    def test(self, condition):
        """ Check if condition is True if self is True.
        """
        if self==condition:
            return True
        r = Equiv(And(self, condition), self)
        return r

    def conditions(self, type=None):
        if type is None: type = Condition
        else: assert issubclass(type, Condition),`type`
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

boolean_classes = (Predicate, Boolean, bool)
Predicate.signature = FunctionSignature(None, boolean_classes)


class And(Predicate):
    """ And(..) predicate.
    """

    signature = FunctionSignature(list(boolean_classes), boolean_classes)

    @classmethod
    def canonize(cls, operants):
        if not operants:
            return True
        if len(operants)==1:
            arg = operants[0]
            if isinstance(arg, bool):
                return arg
            return arg
        new_operants = []
        flag = False
        for o in operants:
            if isinstance(o, bool):
                flag = True
                if not o: return False
            elif o.is_And:
                flag = True
                new_operants.extend(o[:])
            else:
                if o not in new_operants:
                    p = Not(o)
                    if p in new_operants:
                        return False
                    new_operants.append(o)
                else:
                    flag = True
        if flag:
            return cls(*new_operants)
        return

class Or(Predicate):

    signature = FunctionSignature(list(boolean_classes), boolean_classes)

    @classmethod
    def canonize(cls, operants):
        if not operants:
            return True
        if len(operants)==1:
            arg = operants[0]
            if isinstance(arg, bool):
                return arg
            return arg
        new_operants = []
        flag = False
        for o in operants:
            if isinstance(o, bool):
                flag = True
                if o: return True
            elif o.is_Or:
                flag = True
                new_operants.extend(o[:])
            else:
                if o not in new_operants:
                    p = Not(o)
                    if p in new_operants:
                        new_operants.remove(p)
                        flag = True
                    else:
                        new_operants.append(o)
                else:
                    flag = True
        if flag:
            if not new_operants:
                return False
            return cls(*new_operants)
        return

class XOr(Predicate):

    signature = FunctionSignature(list(boolean_classes), boolean_classes)

    @classmethod
    def canonize(cls, operants):
        if not operants:
            return False
        if len(operants)==1:
            arg = operants[0]
            if isinstance(arg, bool):
                return arg
            return arg
        new_operants = []        
        flag = False
        truth_index = 0
        for o in operants:
            if isinstance(o, bool):
                flag = True
                if o: truth_index +=1
                else: pass
            elif o.is_Or:
                flag = True
                new_operants.extend(o[:])
            else:
                if o not in new_operants:
                    po = Not(o)
                    if po in new_operants:
                        flag = True
                        truth_index += 1
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

class Not(Predicate):

    signature = FunctionSignature((boolean_classes,), boolean_classes)

    @classmethod
    def canonize(cls, (arg,)):
        if isinstance(arg, bool):
            return not arg
        if arg.is_Not:
            return arg.args[0]

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

    def __eq2__(self, other):
        if isinstance(other, Basic):
            if not other.is_Equal: return False
            return self[:]==other[:] or (self.lhs==other.rhs and self.rhs==other.lhs)
        if isinstance(other, bool):
            return False
        return self==sympify(other)

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
        
