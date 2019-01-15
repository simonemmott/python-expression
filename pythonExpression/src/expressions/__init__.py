from enum import Enum
from expressions.pypath.tokeniser import TokenType
from importlib.resources import path
import logging

logger = logging.getLogger(__name__)

class ExpressionError(Exception):
    pass

reserved_words = {}
def reserved():
    return reserved_words

def reserved_word(word):
    def decorator(cls):
        reserved_words[word.upper()] = cls
        return cls
    return decorator

class Expression(object): 
    def evaluate(self, src, **params):
        raise NotImplementedError('The evaluate method on class % has not been implemented' % self.__class__.__name__)
    
    def to_path(self):
        raise NotImplementedError('The expression %s does not implement the to_path() method' % self.__class__.__name__)
    
    def __str__(self):
        return 'Expression({expr}) - {path}'.format(expr=self.__class__.__name__, path=self.to_path())
        
class Field(Expression):
    field = None
    list_index = None
    list_filter = None
    def __init__(self, field, *list_key):
        self.field = field
        if len(list_key) == 1:
            filt = list_key[0]
            try:
                self.list_index = int(filt)
                self.list_filter = None
            except:
                if isinstance(filt, Filter) and isinstance(filt.filter, Literal) and isinstance(filt.filter.literal, int):
                    self.list_index = filt.filter.literal
                    self.list_filter = None
                else:
                    self.list_index = None
                    self.list_filter = filt
        elif len(list_key) > 1:
            raise ValueError('Unexpected number of args. %d'%len(list_key))
        else:
            self.list_index = None
            self.list_filter = None
            
    def evaluate(self, src, **params):
        if src == None:
            return None
        if isinstance(src, list):
            lst = []
            for s in src:
                elm = Field._evaluate_single_src(self, s, **params)
                if isinstance(elm, list):
                    lst.extend(elm)
                else:
                    lst.append(elm)
            if len(lst) == 1:
                return lst[0]
            return lst
        else:
            return Field._evaluate_single_src(self, src, **params)
            
    def _evaluate_single_src(self, src, **params):
        if hasattr(src, self.field):
            field = getattr(src, self.field)
        elif hasattr(src, '_'+self.field):
            field = getattr(src, '_'+self.field)
        elif isinstance(src, dict):
            return self._filter_return_value(src.get(self.field))
        else:
            raise ExpressionError('No attribute named {attr} exists on source object with class: {cls}'.format(cls=src.__class__.__name__, attr=self.field))
        if field == None:
            return None
        elif callable(field):
            return self._filter_return_value(field())
        return self._filter_return_value(field, **params)
    
    def _filter_return_value(self, rval, **params):
        if isinstance(rval, list):
            if self.list_index:
                return rval[self.list_index]
            if self.list_filter:
                lst = []
                for item in rval:
                    if self.list_filter.evaluate(item, **params):
                        lst.append(item)
                if len(lst) == 1:
                    return lst[0]
                return lst
        return rval
    
    def to_path(self):
        path = self.field
        if self.list_index:
            return path+TokenType.START_FILTER.value+str(self.list_index)+TokenType.END_FILTER.value
        if self.list_filter:
            return path+self.list_filter.to_path()
        return path

class Path(Field):
    path = None
    def __init__(self, path, field, *list_key):
        Field.__init__(self, field, *list_key)
        if isinstance(path, Field):
            self.path = path
        else:
            raise ValueError('The path must be an instance of the Field class')
            
    def evaluate(self, src, **params):
        if src == None:
            return None
        if isinstance(src, list):
            lst = []
            for s in src:
                elm = Path._evaluate_single_src(self, s, **params)
                if isinstance(elm, list):
                    lst.extend(elm)
                else:
                    lst.append(elm)
            if len(lst) == 1:
                return lst[0]
            return lst
        else:
            return Path._evaluate_single_src(self, src, **params)
            
    def _evaluate_single_src(self, src, **params):
        if self.path:
            result = self.path.evaluate(src, **params)
            return Field.evaluate(self, result, **params)
        else:
            return Field.evaluate(self, src, **params)
        
    def to_path(self):
        if self.path:
            return self.path.to_path()+TokenType.PATH_SEPARATOR.value+Field.to_path(self)
        return Field.to_path(self)
        
class Literal(Expression):
    literal = None
    def __init__(self, literal):
        self.literal = literal
            
    def evaluate(self, src, **params):
        return self.literal
    
    def to_path(self):
        if isinstance(self.literal, str):
            return TokenType.QUOTE.value+self.literal+TokenType.QUOTE.value
        if isinstance(self.literal, int):
            return str(self.literal)
        if isinstance(self.literal, float):
            return str(self.literal)
        if isinstance(self.literal, bool):
            if self.literal:
                return 'True'
            else:
                return 'False'

    
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
    
    def to_path(self):
        return TokenType.PARAMETER.value+self.parameter
        
class Comparator(Expression):
    lhs = None
    rhs = None
    def __init__(self, lhs, rhs):
        self.lhs = lhs
        self.rhs = rhs
            
class Equals(Comparator):
    def evaluate(self, src, **params):
        return self.lhs.evaluate(src, **params) == self.rhs.evaluate(src, **params)
    def to_path(self):
        return self.lhs.to_path()+TokenType.COMPARATOR_EQUAL.value+self.rhs.to_path()
        
class NotEquals(Comparator):
    def evaluate(self, src, **params):
        return self.lhs.evaluate(src, **params) != self.rhs.evaluate(src, **params)
    def to_path(self):
        return self.lhs.to_path()+TokenType.COMPARATOR_NE.value+self.rhs.to_path()
        
class GreaterThan(Comparator):
    def evaluate(self, src, **params):
        return self.lhs.evaluate(src, **params) > self.rhs.evaluate(src, **params)
    def to_path(self):
        return self.lhs.to_path()+TokenType.COMPARATOR_GT.value+self.rhs.to_path()
        
class LessThan(Comparator):
    def evaluate(self, src, **params):
        return self.lhs.evaluate(src, **params) < self.rhs.evaluate(src, **params)
    def to_path(self):
        return self.lhs.to_path()+TokenType.COMPARATOR_LT.value+self.rhs.to_path()
        
class GreaterThanOrEqual(Comparator):
    def evaluate(self, src, **params):
        return self.lhs.evaluate(src, **params) >= self.rhs.evaluate(src, **params)
    def to_path(self):
        return self.lhs.to_path()+TokenType.COMPARATOR_GE.value+self.rhs.to_path()
        
class LessThanOrEqual(Comparator):
    def evaluate(self, src, **params):
        return self.lhs.evaluate(src, **params) <= self.rhs.evaluate(src, **params)
    def to_path(self):
        return self.lhs.to_path()+TokenType.COMPARATOR_LE.value+self.rhs.to_path()
 
@reserved_word('IsNull')   
class IsNull(Expression):
    operand = None
    def __init__(self, operand):
        self.operand = operand
            
    def evaluate(self, src, **params):
        val = self.operand.evaluate(src, **params)
        if val != None:
            if isinstance(val, list):
                if len(val) == 0:
                    return True
                else:
                    return False
            return False
        return True
    
    def to_path(self):
        return ' IsNull'+TokenType.START_GROUP.value+self.operand.to_path()+TokenType.END_GROUP.value
    
    @staticmethod
    def parse(group):
        return IsNull(group.items[0])

@reserved_word('IsNotNull')
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
            return True
        return False
    
    def to_path(self):
        return ' IsNotNull'+TokenType.START_GROUP.value+self.operand.to_path()+TokenType.END_GROUP.value
    
    @staticmethod
    def parse(group):
        return IsNotNull(group.items[0])

    
class Filter(Expression):
    filter = None
    def __init__(self, filter):
        self.filter = filter
        
    def evaluate(self, src, **params):
        if self.filter:
            if self.filter.evaluate(src, **params):
                return src
        return None
        
    def to_path(self):
        return TokenType.START_FILTER.value+self.filter.to_path()+TokenType.END_FILTER.value
    

class Group(Expression):
    items = []
    def __init__(self, *items):
        self.items = items
        
    def extend(self, item):
        self.items.append(item)

    def evaluate(self, src, **params):
        rval = ()
        for item in self.items:
            rval = rval + (item.evaluate(src, **params),)
        return rval
    
    def to_path(self):
        path = TokenType.START_GROUP.value
        for idx, item in enumerate(self.items):
            path = path + item.to_path()
            if idx < len(self.items)-1:
                path = path + TokenType.GROUP_SEPARATOR.value
        path = path + TokenType.END_GROUP.value
        return path
    

class Add(Group):
    def evaluate(self, src, **params):
        val = 0
        for item in self.items:
            item_val = item.evaluate(src, **params)
            if item_val:
                val += item_val
        return val
    
    def to_path(self):
        path = ''
        for idx, item in enumerate(self.items):
            path = path + item.to_path()
            if idx < len(self.items)-1:
                path = path + TokenType.OPERATOR_PLUS.value
        return path
    
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

    def to_path(self):
        path = ''
        for idx, item in enumerate(self.items):
            path = path + item.to_path()
            if idx < len(self.items)-1:
                path = path +TokenType.OPERATOR_MINUS.value
        return path
    
        
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

    def to_path(self):
        path = ''
        for idx, item in enumerate(self.items):
            path = path + item.to_path()
            if idx < len(self.items)-1:
                path = path +TokenType.OPERATOR_MULTIPLY.value
        return path
    
        
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

    def to_path(self):
        path = ''
        for idx, item in enumerate(self.items):
            path = path + item.to_path()
            if idx < len(self.items)-1:
                path = path +TokenType.OPERATOR_DIVIDE.value
        return path
    
@reserved_word('Concat')        
class Concatenate(Group):
    def evaluate(self, src, **params):
        val = ''
        for item in self.items:
            item_val = item.evaluate(src, **params)
            if item_val:
                val += str(item_val)
        return val
    
    def to_path(self):
        path = ' Concat'+TokenType.START_GROUP.value
        for idx, item in enumerate(self.items):
            path = path + item.to_path()
            if idx < len(self.items)-1:
                path = path +TokenType.GROUP_SEPARATOR.value
        path = path + TokenType.END_GROUP.value
        return path
    
    @staticmethod
    def parse(group):
        items = group.items
        return Concatenate(*items)

    
class And(Group):
    def evaluate(self, src, **params):
        if self.items:
            for predicate in self.items:
                if not predicate.evaluate(src, **params):
                    return False
            return True
        return False

    def to_path(self):
        path = TokenType.START_GROUP.value
        for idx, item in enumerate(self.items):
            path = path + item.to_path()
            if idx < len(self.items)-1:
                path = path +TokenType.AND_SEPARATOR.value
        path = path + TokenType.END_GROUP.value
        return path
    

class Or(Group):
    def evaluate(self, src, **params):
        if self.items:
            for predicate in self.items:
                if predicate.evaluate(src, **params):
                    return True
            return False
        return False

    def to_path(self):
        path = TokenType.START_GROUP.value
        for idx, item in enumerate(self.items):
            path = path + item.to_path()
            if idx < len(self.items)-1:
                path = path +TokenType.OR_SEPARATOR.value
        path = path + TokenType.END_GROUP.value
        return path
    

class Not(Expression):
    predicate = None
    def __init__(self, predicate):
        self.predicate = predicate
    def evaluate(self, src, **params):
        return not self.predicate.evaluate(src, **params)
    
    def to_path(self):
        return TokenType.NOT.value+self.predicate.to_path()







        