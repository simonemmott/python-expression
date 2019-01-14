'''
Created on 28 Dec 2018

@author: simon
'''
import re
#from expressions import Path, Field, Equals, NotEquals, GreaterThan, GreaterThanOrEqual, LessThan, LessThanOrEqual, Add, Subtract, Divide, Multiply, Or, And, Group, Not, Literal, Parameter
import expressions
from enum import Enum
from expressions.pypath.tokeniser import TokenType, PyPathError

class GroupType(Enum):
    AND = 'AND'
    OR = 'OR'
    TUPLE = 'TUPLE'
    
class ExpressionParser(object):
    def __init__(self, tokeniser, reserved=None):
        self.tokeniser = tokeniser
        self.expression = None
        if reserved:
            self.reserved = reserved
        else:
            self.reserved = expressions.reserved_words
        self.word = None
        
    def is_reserved_word(self, word):
        return word.upper() in self.reserved
    
          
    def get_expression(self):
        
        lhs = self.get_compound_expression()
        peek = self.tokeniser.peek_next_token()
        if peek and peek.is_comparator():
            comp = self.tokeniser.get_next_token()
            rhs = self.get_compound_expression()
            if comp.token_type == TokenType.COMPARATOR_EQUAL:
                return expressions.Equals(lhs, rhs)
            elif comp.token_type == TokenType.COMPARATOR_NE:
                return expressions.NotEquals(lhs, rhs)
            elif comp.token_type == TokenType.COMPARATOR_GT:
                return expressions.GreaterThan(lhs, rhs)
            elif comp.token_type == TokenType.COMPARATOR_GE:
                return expressions.GreaterThanOrEqual(lhs, rhs)
            elif comp.token_type == TokenType.COMPARATOR_LT:
                return expressions.LessThan(lhs, rhs)
            elif comp.token_type == TokenType.COMPARATOR_LE:
                return expressions.LessThanOrEqual(lhs, rhs)
            else:
                raise PyPathError('Unexpected comparator: %s'%comp.token_type.value,
                                  self.tokeniser.pos,
                                  self.tokeniser.row,
                                  self.tokeniser.col)
        return lhs
            
        
    def get_compound_expression(self):
        lhs = self.get_base_expression()
        peek = self.tokeniser.peek_next_token()
        while peek and peek.is_operator():
            oper = self.tokeniser.get_next_token()
            rhs = self.get_base_expression()
            if oper.token_type == TokenType.OPERATOR_PLUS:
                lhs = expressions.Add(lhs, rhs)
            elif oper.token_type == TokenType.OPERATOR_MINUS:
                lhs = expressions.Subtract(lhs, rhs)
            elif oper.token_type == TokenType.OPERATOR_DIVIDE:
                lhs = expressions.Divide(lhs, rhs)
            elif oper.token_type == TokenType.OPERATOR_MULTIPLY:
                lhs = expressions.Multiply(lhs, rhs)
            else:
                raise PyPathError('Unexpected operator: %s'%oper.token_type.value,
                                  self.tokeniser.pos,
                                  self.tokeniser.row,
                                  self.tokeniser.col)
            peek = self.tokeniser.peek_next_token()
        return lhs
        
    def get_base_expression(self):
        exp = None
        t = self.tokeniser.get_next_token()
        
        while t:
            if t.token_type == TokenType.START_FILTER:
                f = self.get_expression()
                peek = self.tokeniser.peek_next_token()
                if peek.token_type == TokenType.END_FILTER:
                    self.tokeniser.get_next_token()
                    return expressions.Filter(f)
                raise PyPathError('Unexpected token: %s'%t.token_type.value,
                                  self.tokeniser.pos,
                                  self.tokeniser.row,
                                  self.tokeniser.col)
            
            if t.token_type == TokenType.END_FILTER:
                raise PyPathError('Unexpected End Filter: %s'%t.token_type.value,
                                  self.tokeniser.pos,
                                  self.tokeniser.row,
                                  self.tokeniser.col)
            
            elif t.token_type == TokenType.START_GROUP:
                items = []
                group_type = None
                peek = self.tokeniser.peek_next_token()
                while peek and peek.token_type not in [TokenType.GROUP_SEPARATOR,
                                                   TokenType.END_GROUP]:
                    items.append(self.get_expression())
                    peek = self.tokeniser.peek_next_token()
                    if peek.token_type == TokenType.GROUP_SEPARATOR:
                        t = self.tokeniser.get_next_token()
                        peek = self.tokeniser.peek_next_token()
                        if not group_type:
                            group_type = GroupType.TUPLE
                        elif group_type != GroupType.TUPLE:
                            raise PyPathError('Unexpected token: %s'%t.token_type.value,
                                              self.tokeniser.pos,
                                              self.tokeniser.row,
                                              self.tokeniser.col)
                    elif peek.token_type == TokenType.AND_SEPARATOR:
                        t = self.tokeniser.get_next_token()
                        peek = self.tokeniser.peek_next_token()
                        if not group_type:
                            group_type = GroupType.AND
                        elif group_type != GroupType.AND:
                            raise PyPathError('Unexpected token: %s'%t.token_type.value,
                                              self.tokeniser.pos,
                                              self.tokeniser.row,
                                              self.tokeniser.col)
                    elif peek.token_type == TokenType.OR_SEPARATOR:
                        t = self.tokeniser.get_next_token()
                        peek = self.tokeniser.peek_next_token()
                        if not group_type:
                            group_type = GroupType.OR
                        elif group_type != GroupType.OR:
                            raise PyPathError('Unexpected token: %s'%t.token_type.value,
                                              self.tokeniser.pos,
                                              self.tokeniser.row,
                                              self.tokeniser.col)
                    elif peek.token_type != TokenType.END_GROUP:
                        raise PyPathError('Unexpected token: %s'%t.token_type.value,
                                          self.tokeniser.pos,
                                          self.tokeniser.row,
                                          self.tokeniser.col)
                if peek.token_type == TokenType.END_GROUP:
                    t = self.tokeniser.get_next_token()
                    if group_type:
                        if group_type == GroupType.TUPLE:
                            return expressions.Group(*items)
                        if group_type == GroupType.AND:
                            return expressions.And(*items)
                        if group_type == GroupType.OR:
                            return expressions.And(*items)
                        raise PyPathError("Unknown group type %s"%group_type,
                                              self.tokeniser.pos,
                                              self.tokeniser.row,
                                              self.tokeniser.col)
                    else:
                        return expressions.Group(*items)
                
                raise PyPathError('Unexpected token: %s'%t.token_type.value,
                                  self.tokeniser.pos,
                                  self.tokeniser.row,
                                  self.tokeniser.col)
            
            elif t.token_type == TokenType.END_GROUP:
                raise PyPathError('Unexpected End Group: %s'%t.token_type.value,
                                  self.tokeniser.pos,
                                  self.tokeniser.row,
                                  self.tokeniser.col)
            
            elif t.token_type == TokenType.NOT:
                if exp == None:
                    return expressions.Not(self.get_expression())
                else:
                    raise PyPathError("Excountered boolean value %s, expecting an operator, group separator or end of group/filter"%t.value, 
                                      self.tokeniser.pos,
                                      self.tokeniser.row,
                                      self.tokeniser.col) 
                
            elif t.is_comparator():
                raise PyPathError('Unexpected comparator: %s'%t.token_type.value,
                                  self.tokeniser.pos,
                                  self.tokeniser.row,
                                  self.tokeniser.col)
            
            elif t.is_operator():
                raise PyPathError('Unexpected operator: %s'%t.token_type.value,
                                  self.tokeniser.pos,
                                  self.tokeniser.row,
                                  self.tokeniser.col)
            
            elif t.is_separator():
                raise PyPathError('Unexpected sepataror: %s'%t.token_type.value,
                                  self.tokeniser.pos,
                                  self.tokeniser.row,
                                  self.tokeniser.col)
            
            elif t.token_type == TokenType.LITERAL_BOOLEAN:
                if exp == None:
                    return expressions.Literal(t.value)
                else:
                    raise PyPathError("Excountered boolean value %s, expecting an operator, group separator or end of group/filter"%t.value, 
                                      self.tokeniser.pos,
                                      self.tokeniser.row,
                                      self.tokeniser.col) 
                                     
            elif t.token_type == TokenType.LITERAL_INT:
                if exp == None:
                    return expressions.Literal(t.value)
                else:
                    raise PyPathError("Excountered integer value %d, expecting an operator, group separator or end of group/filter"%t.value, 
                                      self.tokeniser.pos,
                                      self.tokeniser.row,
                                      self.tokeniser.col)
                    
            elif t.token_type == TokenType.LITERAL_FLOAT:
                if exp == None:
                    return expressions.Literal(t.value)
                else:
                    raise PyPathError("Excountered float value %d, expecting an operator, group separator or end of group/filter"%t.value, 
                                      self.tokeniser.pos,
                                      self.tokeniser.row,
                                      self.tokeniser.col)
                    
            elif t.token_type == TokenType.LITERAL_STRING:
                if exp == None:
                    return expressions.Literal(t.value)
                else:
                    raise PyPathError("Excountered literal string '%s', expecting an operator, group separator or end of group/filter"%t.value, 
                                      self.tokeniser.pos,
                                      self.tokeniser.row,
                                      self.tokeniser.col)
                    
            elif t.token_type == TokenType.PARAMETER:
                if exp == None:
                    return expressions.Parameter(t.value)
                else:
                    raise PyPathError("Excountered parameter '%s', expecting an operator, group separator or end of group/filter"%t.value, 
                                      self.tokeniser.pos,
                                      self.tokeniser.row,
                                      self.tokeniser.col)
                    
            elif t.token_type == TokenType.WORD:
                if self.is_reserved_word(t.value):
                    peek = self.tokeniser.peek_next_token()
                    if peek.token_type == TokenType.START_GROUP:
                        group = self.get_expression()
                        return self.reserved[t.value.upper()].parse(group)
                    return None
                else:
                    group_exp = None
                    peek = self.tokeniser.peek_next_token()
                    if peek and peek.token_type == TokenType.START_FILTER:
                        group_exp = self.get_expression()
                     
                    peek = self.tokeniser.peek_next_token()
                    if peek and peek.token_type == TokenType.PATH_SEPARATOR:
                        self.tokeniser.get_next_token()
                        if exp == None:
                            if group_exp:
                                exp = expressions.Field(t.value, group_exp)
                            else:
                                exp = expressions.Field(t.value)
                        else:
                            if group_exp:
                                exp = expressions.Path(exp, t.value, group_exp)
                            else:
                                exp = expressions.Path(exp, t.value)
                        
                    else:
                        if exp == None:
                            if group_exp:
                                return expressions.Field(t.value, group_exp)
                            else:
                                return expressions.Field(t.value)
                        else:
                            if group_exp:
                                return expressions.Path(exp, t.value, group_exp)
                            else:
                                return expressions.Path(exp, t.value)
        
            t = self.tokeniser.get_next_token()
            peek = self.tokeniser.peek_next_token()
            
            
if __name__ == '__main__':
    f = expressions.Field('aaa')
    print(f.field)