'''
Created on 28 Dec 2018

@author: simon
'''
import re
from expressions import *
from enum import Enum
from expressions.pypath.tokeniser import TokenType, PyPathError

class GroupType(Enum):
    AND = 'AND'
    OR = 'OR'
    PARAMS = 'PARAMS'
    
class ExpressionParser(object):
    def __init__(self, tokeniser, reserved={}):
        self.tokeniser = tokeniser
        self.expression = None
        self.reserved = reserved
        self.word = None
        
    def is_reserved_word(self, word):
        return word in self.reserved
    
          
    def get_expression(self):
        
        lhs = self.get_compound_expression()
        peek = self.tokeniser.peek_next_token()
        if peek and peek.is_comparator():
            comp = self.tokeniser.get_next_token()
            rhs = self.get_compound_expression()
            if comp.token_type == TokenType.COMPARATOR_EQUAL:
                return Equals(lhs, rhs)
            elif comp.token_type == TokenType.COMPARATOR_NE:
                return NotEquals(lhs, rhs)
            elif comp.token_type == TokenType.COMPARATOR_GT:
                return GreaterThan(lhs, rhs)
            elif comp.token_type == TokenType.COMPARATOR_GE:
                return GreaterThanOrEqual(lhs, rhs)
            elif comp.token_type == TokenType.COMPARATOR_LT:
                return LessThan(lhs, rhs)
            elif comp.token_type == TokenType.COMPARATOR_LE:
                return LessThanOrEqual(lhs, rhs)
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
                lhs = Add(lhs, rhs)
            elif oper.token_type == TokenType.OPERATOR_MINUS:
                lhs = Subtract(lhs, rhs)
            elif oper.token_type == TokenType.OPERATOR_DIVIDE:
                lhs = Divide(lhs, rhs)
            elif oper.token_type == TokenType.OPERATOR_MULTIPLY:
                lhs = Multiply(lhs, rhs)
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
                items = []
                filter_type = ''
                peek = self.tokeniser.peek_next_token()
                while peek and peek.token_type not in [TokenType.AND_SEPARATOR,
                                                   TokenType.OR_SEPARATOR,
                                                   TokenType.END_FILTER]:
                    items.append(self.get_expression())
                    peek = self.tokeniser.peek_next_token()
                    if peek.token_type in [TokenType.OR_SEPARATOR,
                                           TokenType.AND_SEPARATOR]:
                        if peek.token_type == TokenType.AND_SEPARATOR:
                            if filter_type == '' or filter_type == 'AND':
                                filter_type = 'AND'
                            else:
                                raise PyPathError('Ambiguous logical grouping: %s'%t.token_type.value,
                                                  self.tokeniser.pos,
                                                  self.tokeniser.row,
                                                  self.tokeniser.col)
                        else:
                            if filter_type == '' or filter_type == 'OR':
                                filter_type = 'OR'
                            else:
                                raise PyPathError('Ambiguous logical grouping: %s'%t.token_type.value,
                                                  self.tokeniser.pos,
                                                  self.tokeniser.row,
                                                  self.tokeniser.col)
                            
                        self.tokeniser.get_next_token()
                        peek = self.tokeniser.peek_next_token()
                    elif peek.token_type != TokenType.END_FILTER:
                        raise PyPathError('Unexpected token: %s'%t.token_type.value,
                                          self.tokeniser.pos,
                                          self.tokeniser.row,
                                          self.tokeniser.col)
                if peek.token_type == TokenType.END_FILTER:
                    self.tokeniser.get_next_token()
                    if filter_type == 'OR':
                        return Or(*items)
                    else:
                        return And(*items)
                
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
                peek = self.tokeniser.peek_next_token()
                while peek and peek.token_type not in [TokenType.GROUP_SEPARATOR,
                                                   TokenType.END_GROUP]:
                    items.append(self.get_expression())
                    peek = self.tokeniser.peek_next_token()
                    if peek.token_type == TokenType.GROUP_SEPARATOR:
                        self.tokeniser.get_next_token()
                        peek = self.tokeniser.peek_next_token()
                    elif peek.token_type != TokenType.END_GROUP:
                        raise PyPathError('Unexpected token: %s'%t.token_type.value,
                                          self.tokeniser.pos,
                                          self.tokeniser.row,
                                          self.tokeniser.col)
                if peek.token_type == TokenType.END_GROUP:
                    self.tokeniser.get_next_token()
                    return Group(*items)
                
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
                    return Not(self.get_expression())
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
                    return Literal(t.value)
                else:
                    raise PyPathError("Excountered boolean value %s, expecting an operator, group separator or end of group/filter"%t.value, 
                                      self.tokeniser.pos,
                                      self.tokeniser.row,
                                      self.tokeniser.col) 
                                     
            elif t.token_type == TokenType.LITERAL_INT:
                if exp == None:
                    return Literal(t.value)
                else:
                    raise PyPathError("Excountered integer value %d, expecting an operator, group separator or end of group/filter"%t.value, 
                                      self.tokeniser.pos,
                                      self.tokeniser.row,
                                      self.tokeniser.col)
                    
            elif t.token_type == TokenType.LITERAL_FLOAT:
                if exp == None:
                    return Literal(t.value)
                else:
                    raise PyPathError("Excountered float value %d, expecting an operator, group separator or end of group/filter"%t.value, 
                                      self.tokeniser.pos,
                                      self.tokeniser.row,
                                      self.tokeniser.col)
                    
            elif t.token_type == TokenType.LITERAL_STRING:
                if exp == None:
                    return Literal(t.value)
                else:
                    raise PyPathError("Excountered literal string '%s', expecting an operator, group separator or end of group/filter"%t.value, 
                                      self.tokeniser.pos,
                                      self.tokeniser.row,
                                      self.tokeniser.col)
                    
            elif t.token_type == TokenType.PARAMETER:
                if exp == None:
                    return Parameter(t.value)
                else:
                    raise PyPathError("Excountered parameter '%s', expecting an operator, group separator or end of group/filter"%t.value, 
                                      self.tokeniser.pos,
                                      self.tokeniser.row,
                                      self.tokeniser.col)
                    
            elif t.token_type == TokenType.WORD:
                if self.is_reserved_word(t.value):
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
                                exp = Field(t.value, group_exp)
                            else:
                                exp = Field(t.value)
                        else:
                            if group_exp:
                                exp = Path(exp, t.value, group_exp)
                            else:
                                exp = Path(exp, t.value)
                        
                    else:
                        if exp == None:
                            if group_exp:
                                return Field(t.value, group_exp)
                            else:
                                return Field(t.value)
                        else:
                            if group_exp:
                                return Path(exp, t.value, group_exp)
                            else:
                                return Path(exp, t.value)
        
            t = self.tokeniser.get_next_token()
            peek = self.tokeniser.peek_next_token()
            