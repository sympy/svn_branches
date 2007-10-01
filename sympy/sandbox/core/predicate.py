
from basic import Basic, Atom
from function import Function, FunctionSignature

class Predicate(Function):
    """ Base class for predicate functions.
    """
    return_canonize_types = (Basic, bool)

Predicate.signature = FunctionSignature(None, (Predicate,bool))

class And(Predicate):

    signature = FunctionSignature([Predicate,bool], (Predicate,bool))

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

    signature = FunctionSignature([Predicate,bool], (Predicate,bool))

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
            return cls(*new_operants)
        return

class XOr(Predicate):

    signature = FunctionSignature([Predicate,bool], (Predicate,bool))

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

    signature = FunctionSignature(((Predicate, bool),), (Predicate,bool))

    @classmethod
    def canonize(cls, (arg,)):
        if isinstance(arg, bool):
            return not arg
        if arg.is_Not:
            return arg.args[0]

class Implies(Predicate):
    signature = FunctionSignature(((Predicate,bool),(Predicate,bool)), (Predicate,bool))

    @classmethod
    def canonize(cls, (lhs, rhs)):
        return Or(Not(lhs), rhs)

class Equiv(Predicate):
    signature = FunctionSignature(((Predicate,bool), (Predicate,bool)), (Predicate,bool))

    @classmethod
    def canonize(cls, (lhs, rhs)):
        return Not(XOr(lhs, rhs))

class Equal(Predicate):

    signature = FunctionSignature((Basic, Basic), (Predicate,bool))

    @classmethod
    def canonize(cls, (lhs, rhs)):
        if lhs==rhs: return True
        if lhs.is_Number and rhs.is_Number: return False

class Less(Predicate):

    signature = FunctionSignature((Basic, Basic), (Predicate,bool))
    
    @classmethod
    def canonize(cls, (lhs, rhs)):
        if lhs.is_Number and rhs.is_Number:
            return lhs < rhs
        elif lhs==rhs: return False

class IsReal(Predicate):
    
    signature = FunctionSignature((Basic,), (Predicate,bool))
    
    @classmethod
    def canonize(cls, (arg,)):
        if arg.is_Real: return True
        if arg.is_Number: return False
        if arg.is_ImaginaryUnit: return False

class IsRational(IsReal):
    
    signature = FunctionSignature((Basic,), (Predicate,bool))
    
    @classmethod
    def canonize(cls, (arg,)):
        if arg.is_Rational: return True
        if arg.is_Number: return False

class IsInteger(IsRational):
    
    signature = FunctionSignature((Basic,), (Predicate,bool))
    
    @classmethod
    def canonize(cls, (arg,)):
        if arg.is_Integer: return True
        if arg.is_Number: return False

class IsPositive(IsReal):
    
    signature = FunctionSignature((Basic,), (Predicate,bool))
    
    @classmethod
    def canonize(cls, (arg,)):
        return And(IsReal(arg),Less(0, arg))

class IsNegative(IsReal):
    
    signature = FunctionSignature((Basic,), (Predicate,bool))
    
    @classmethod
    def canonize(cls, (arg,)):
        return And(IsReal(arg),Less(arg, 0))
        
