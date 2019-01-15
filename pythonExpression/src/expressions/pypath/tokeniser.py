'''
Created on 31 Dec 2018

@author: simon
'''
from enum import Enum
from utilities import numUtil
import re
import logging

logger = logging.getLogger(__name__)

RE_SPACE = re.compile('\s')

class PyPathError(Exception):
    def __init__(self, msg, pos, row, col):
        Exception.__init__(self, '{msg} at position: {pos} row: {row} col: {col}'.format(msg=msg, pos=pos, row=row, col=col))
    pass

class TokenType(Enum):
    START_GROUP = '('
    END_GROUP = ')'
    GROUP_SEPARATOR = ','
    AND_SEPARATOR = '&'
    OR_SEPARATOR = '|'
    PATH_SEPARATOR = '.'
    PARAMETER = '$'
    PATH_ROOT = ':'
    NOT = '!'
    START_FILTER = '['
    END_FILTER = ']'
    COMPARATOR_EQUAL = '=='
    COMPARATOR_GT = '>'
    COMPARATOR_GE = '>='
    COMPARATOR_LT = '<'
    COMPARATOR_LE = "<="
    COMPARATOR_NE = '!='
    OPERATOR_PLUS = '+'
    OPERATOR_MINUS = '-'
    OPERATOR_MULTIPLY = '*'
    OPERATOR_DIVIDE = '/'
    WORD = '_'
    LITERAL_STRING = 'STR'
    LITERAL_INT = 'INT'
    LITERAL_FLOAT = 'FLOAT'
    LITERAL_BOOLEAN = 'BOOL'
    QUOTE = '"'
    
    
class Token(object):
    def __init__(self, token_type, value=None):
        self.token_type = token_type
        self.value = value
        
    def is_comparator(self):
        return self.token_type in [TokenType.COMPARATOR_EQUAL,
                                   TokenType.COMPARATOR_NE,
                                   TokenType.COMPARATOR_GT,
                                   TokenType.COMPARATOR_GE,
                                   TokenType.COMPARATOR_LT,
                                   TokenType.COMPARATOR_LE]
    def is_operator(self):
        return self.token_type in [TokenType.OPERATOR_PLUS,
                                   TokenType.OPERATOR_MINUS,
                                   TokenType.OPERATOR_MULTIPLY,
                                   TokenType.OPERATOR_DIVIDE]  
    
    def is_separator(self):
        return self.token_type in [TokenType.GROUP_SEPARATOR,
                                   TokenType.AND_SEPARATOR,
                                   TokenType.OR_SEPARATOR,
                                   TokenType.PATH_SEPARATOR] 
    
    def __str__(self):
        if self.value:
            return self.token_type.name+'('+str(self.value)+')'
        return self.token_type.name+'()'
    
class Tokeniser(object):
    def __init__(self, reader, **kw):
        self.reader = reader
        self.path = ''
        self.pos = 0
        self.row = 0
        self.col = 0
        self.quote = kw.get('quote', TokenType.QUOTE.value)
        self.escape = '\\'
        self.token_value = ''
        self.escaping = False
        self.in_quotes = False
        self.in_number = False
        self.hold = None
        self.last = ''
        self.peek_token = None
        self.peek = self.reader.read(1)
    
    def get_error(self, msg):
        return PyPathError(msg, self.pos, self.row, self.col)
    
    def peek_next_token(self):
        if self.peek_token != None:
            return self.peek_token
        if self.hold != None:
            return self.hold
        self.peek_token = self.get_next_token()
        return self.peek_token
        
        
    def get_next_token(self):
        logger.debug('get_next_token')
        if self.peek_token != None:
            peek = self.peek_token
            self.peek_token = None
            logger.debug('next token: {token}'.format(token=peek))
            return peek
        
        if self.hold != None:
            hold = self.hold
            self.hold = None
            return hold
        
        c = self.peek
        self.peek = self.reader.read(1)
        while c != None:
            token = self.tokenise_char(c)
            self.last = c

            if token != None:
                return token

            c = self.peek
            self.peek = self.reader.read(1)

        return None
    
    def tokenise_char(self, c):
        self.pos += 1
        self.col += 1
        
        if (c == '\n' and not self.in_quotes):
            self.col = 0
            self.row += 1
            
#        print ('pos: {pos} row: {row} col: {col} char:{char}'.format(pos=self.pos, row=self.row, col=self.col, char=c))
        
#        print ('%s %s %s' % (self.last, c, self.peek))
        
        if self.in_quotes:
            if self.escaping:
                if c == 'n':
                    c = '\n'
                elif c == 'b':
                    c = '\b'
                elif c == 'r':
                    c = '\r'
                elif c == 't':
                    c = '\t'
                self.token_value += c
                self.escaping = False
                return
            
            if c == self.escape:
                self.escaping = True
                return
            
            if c == self.quote:
                self.in_quotes = False
                return self.found_token(TokenType.LITERAL_STRING, self.token_value)
            
            self.token_value += c
            return
        
        if c == self.quote:
            self.in_quotes = True
            return

        if self.in_number:
            if c in '0123456789.':
                if c in '0123456789':
                    self.token_value += c
                else:
                    if numUtil.is_int(self.token_value):
                        self.token_value += c
                    else:
                        raise self.get_error('%s%s is not a number' % (self.token_value, c))
                if self.peek == None:
                    if numUtil.is_int(self.token_value):
                        return self.found_token(TokenType.LITERAL_INT, int(self.token_value))
                    else:
                        return self.found_token(TokenType.LITERAL_FLOAT, float(self.token_value))
                return
            else:
                if numUtil.is_int(self.token_value):
                    t = self.found_token(TokenType.LITERAL_INT, int(self.token_value))
                else:
                    t = self.found_token(TokenType.LITERAL_FLOAT, float(self.token_value))
                tt = self.get_token_type(c)
                if tt:
                    self.hold_token(tt)
                return t
            
        if self.token_value == '' and c in '0123456789':
            self.token_value += c
            self.in_number = True
            return
            
        tt = self.get_token_type(c)
        if tt:
            if self.token_value != '':
                self.hold_token(tt)
                return self.found_token(TokenType.WORD, self.token_value)
            return self.found_token(tt)
        
        if not RE_SPACE.match(c+'') and c != '=':
            self.token_value += c
        
        if self.token_value.upper() == 'TRUE': return self.found_token(TokenType.LITERAL_BOOLEAN, True)
        if self.token_value.upper() == 'FALSE': return self.found_token(TokenType.LITERAL_BOOLEAN, False)
        
        if RE_SPACE.match(c+'') and self.token_value != '':
            return self.found_token(TokenType.WORD, self.token_value)
        
        if self.peek == None and self.token_value != '':
            return self.found_token(TokenType.WORD, self.token_value)
        
        return
                
    def get_token_type(self, c):            
        if   c == TokenType.START_GROUP.value:     return TokenType.START_GROUP
        elif c == TokenType.END_GROUP.value:       return TokenType.END_GROUP
        elif c == TokenType.START_FILTER.value:    return TokenType.START_FILTER
        elif c == TokenType.END_FILTER.value:      return TokenType.END_FILTER
        elif c == TokenType.GROUP_SEPARATOR.value: return TokenType.GROUP_SEPARATOR
        elif c == TokenType.AND_SEPARATOR.value:   return TokenType.AND_SEPARATOR
        elif c == TokenType.OR_SEPARATOR.value:    return TokenType.OR_SEPARATOR
        elif c == TokenType.PATH_SEPARATOR.value:  return TokenType.PATH_SEPARATOR
        elif c == TokenType.PATH_ROOT.value:       return TokenType.PATH_ROOT
        elif c == TokenType.NOT.value and self.peek != '=':                 return TokenType.NOT
        elif self.peek and c+self.peek == TokenType.COMPARATOR_EQUAL.value: return TokenType.COMPARATOR_EQUAL
        elif c == TokenType.COMPARATOR_GT.value[0] and self.peek != '=':    return TokenType.COMPARATOR_GT
        elif self.peek and c+self.peek == TokenType.COMPARATOR_GE.value:    return TokenType.COMPARATOR_GE
        elif c == TokenType.COMPARATOR_LT.value[0] and self.peek != '=':    return TokenType.COMPARATOR_LT
        elif self.peek and c+self.peek == TokenType.COMPARATOR_LE.value:    return TokenType.COMPARATOR_LE
        elif self.peek and c+self.peek == TokenType.COMPARATOR_NE.value:    return TokenType.COMPARATOR_NE
        elif c == TokenType.OPERATOR_PLUS.value:     return TokenType.OPERATOR_PLUS
        elif c == TokenType.OPERATOR_MINUS.value:    return TokenType.OPERATOR_MINUS
        elif c == TokenType.OPERATOR_DIVIDE.value:   return TokenType.OPERATOR_DIVIDE
        elif c == TokenType.OPERATOR_MULTIPLY.value: return TokenType.OPERATOR_MULTIPLY
        else:
            return None
         
    def hold_token(self, token_type, value=None):
        self.hold = Token(token_type, value)
          
    def found_token(self, token_type, value=None):
        self.token_value = ''
        self.in_quotes = False
        self.in_number = False
        self.escaping = False
        if token_type == TokenType.WORD and value and isinstance(value, str) and len(value)>1 and value[0] == TokenType.PARAMETER.value:
            return Token(TokenType.PARAMETER, value[1:])
        return Token(token_type, value)
        
            

        