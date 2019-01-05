from enum import Enum

class Expression(object): 
    def evaluate(self, src, **params):
        if src == None:
            return None
        if isinstance(src, list):
            lst = []
            for s in src:
                elm = self._evaluate_single_src(s, **params)
                if isinstance(elm, list):
                    lst.extend(elm)
                else:
                    lst.append(elm)
            return lst
        else:
            return self._evaluate_single_src(src, **params)
            
    def _evaluate_single_src(self, src, **params):
        raise NotImplementedError('The evaluate_single_src method on class % has not been implemented' % self.__class__.__name__)
        
class Field(Expression):
    field = None
    list_index = None
    list_eval = None
    def __init__(self, field, *list_key):
        self.field = field
        if len(list_key) == 1:
            try:
                self.list_index = int(list_key[0])
                self.list_keys = None
            except ValueError:
                self.list_index = None
                self.list_key = list_key[0]
        elif len(list_key) > 1:
            raise ValueError('Unexpected number of args. %d'%len(list_key))
        else:
            self.list_index = None
            self.list_keys = None
            
            
    def _evaluate_single_src(self, src, **params):
        if hasattr(src, self.field):
            field = getattr(src, self.field)
        elif hasattr(src, '_'+self.field):
            field = getattr(src, '_'+self.field)
        else:
            return self._filter_return_value(self.get(self.field))
        if field == None:
            return None
        elif callable(field):
            return self._filter_return_value(field())
        return self._filter_return_value(field)
    
    def _filter_return_value(self, rval):
        if isinstance(rval, list):
            if self.list_index:
                return rval[self.list_index]
            lst = []
            for item in rval:
                if self.list_key.evaluate(item):
                    lst.append(item)
            return lst
        return rval

class Path(Field):
    path = None
    def __init__(self, path, field, *list_key):
        Field.__init__(self, field, *list_key)
        if isinstance(path, Field):
            self.path = path
        else:
            raise ValueError('The path must be an instance of the Field class')
            
    def _evaluate_single_src(self, src, **params):
        if self.path:
            return Field.evaluate(self, self.path.evaluate(src, **params), **params)
        else:
            return Field.evaluate(src, **params)
        
class Literal(Expression):
    literal = None
    def __init__(self, literal):
        self.literal = literal
            
    def evaluate(self, src, **params):
        return self.literal
    
class ParameterValue(Enum):
    NOT_SET=0
        
class Parameter(Expression):
    parameter = None
    def __init__(self, parameter):
        self.parameter = parameter
            
    def evaluate(self, src, **params):
        val = params.get(self.parameter, ParameterValue.NOT_SET)
        if val != ParameterValue.NOT_SET:
            return val
        raise ValueError('The parameter named: %s was not set' % self.parameter)
        
class Comparator(Expression):
    lhs = None
    rhs = None
    def __init__(self, lhs, rhs):
        self.lhs = lhs
        self.rhs = rhs
            
class Equals(Comparator):
    def evaluate(self, src, **params):
        return self.lhs.evaluate(src, **params) == self.rhs.evaluate(src, **params)
        
class NotEquals(Comparator):
    def evaluate(self, src, **params):
        return self.lhs.evaluate(src, **params) != self.rhs.evaluate(src, **params)
        
class GreaterThan(Comparator):
    def evaluate(self, src, **params):
        return self.lhs.evaluate(src, **params) > self.rhs.evaluate(src, **params)
        
class LessThan(Comparator):
    def evaluate(self, src, **params):
        return self.lhs.evaluate(src, **params) < self.rhs.evaluate(src, **params)
        
class GreaterThanOrEqual(Comparator):
    def evaluate(self, src, **params):
        return self.lhs.evaluate(src, **params) >= self.rhs.evaluate(src, **params)
        
class LessThanOrEqual(Comparator):
    def evaluate(self, src, **params):
        return self.lhs.evaluate(src, **params) <= self.rhs.evaluate(src, **params)
    
class IsNull(Expression):
    operand = None
    def __init__(self, operand):
        self.operand = operand
            
    def evaluate(self, src, **params):
        val = self.operand.evaluate(src, **params)
        if val:
            if isinstance(val, list):
                if len(val) == 0:
                    return True
                else:
                    return False
            return True
        return False

class IsNotNull(Expression):
    operand = None
    def __init__(self, operand):
        self.operand = operand
            
    def evaluate(self, src, **params):
        val = self.operand.evaluate(src, **params)
        if val:
            if isinstance(val, list):
                if len(val) == 0:
                    return False
                else:
                    return True
            return False
        return True

class Group(Expression):
    items = []
    def __init__(self, *items):
        self.items = items
        
    def extend(self, item):
        self.items.append(item)

class Add(Group):
    def evaluate(self, src, **params):
        val = 0
        for item in self.items:
            item_val = item.evaluate(src, **params)
            if item_val:
                val += item_val
        return val
        
class Subtract(Group):
    def evaluate(self, src, **params):
        val = None
        for item in self.items:
            item_val = item.evaluate(src, **params)
            if val:
                if item_val:
                    val -= item_val
            else:
                if item_val:
                    val = item_val
                else:
                    val = 0
        return val
        
class Multiply(Group):
    def evaluate(self, src, **params):
        val = None
        for item in self.items:
            item_val = item.evaluate(src, **params)
            if val:
                if item_val:
                    val *= item_val
            else:
                if item_val:
                    val = item_val
                else:
                    val = 0
        return val
        
class Divide(Group):
    def evaluate(self, src, **params):
        val = None
        for item in self.items:
            item_val = item.evaluate(src, **params)
            if val:
                if not item_val or item_val == 0:
                    raise ZeroDivisionError
                else:
                    val /= item_val
            else:
                if item_val:
                    val = item_val
                else:
                    val = 0
        return val
        
class Concatenate(Group):
    def evaluate(self, src, **params):
        val = ''
        for item in self.items:
            item_val = item.evaluate(src, **params)
            if item_val:
                val += item_val
        return val
    
class And(Group):
    def evaluate(self, src, **params):
        if self.items:
            for predicate in self.items:
                if not predicate.evaluate(src, **params):
                    return False
            return True
        return False

class Or(Group):
    def evaluate(self, src, **params):
        if self.items:
            for predicate in self.items:
                if predicate.evaluate(src, **params):
                    return True
            return False
        return False

class Not(Expression):
    predicate = None
    def __init__(self, predicate):
        self.predicate = predicate
    def evaluate(self, src, **params):
        return not self.predicate.evaluate(src, **params)







        