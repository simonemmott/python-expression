'''
Created on 28 Dec 2018

@author: simon
'''
import unittest
from utilities.readers import StringReader
from expressions.pypath import tokeniser
from expressions.pypath.tokeniser import Tokeniser


class TestTokeniser(unittest.TestCase):

    def test_get_next_token(self):
        tkns = Tokeniser(StringReader('aaa.bbb.ccc.ddd'))
        t = tkns.get_next_token()
        while t:
            print('Token type: %s Value: %s' % (t.token_type, t.value))
            t = tkns.get_next_token()


    def test_path(self):
        
        tkns = Tokeniser(StringReader('aaa.bbb.ccc.ddd'))
        
        t = tkns.get_next_token()
        self.assertNotEqual(None, t)
        self.assertEqual(tokeniser.TokenType.WORD, t.token_type)
        self.assertEqual('aaa', t.value)
        
        t = tkns.get_next_token()
        self.assertEqual(tokeniser.TokenType.PATH_SEPARATOR, t.token_type)

        t = tkns.get_next_token()
        self.assertEqual(tokeniser.TokenType.WORD, t.token_type)
        self.assertEqual('bbb', t.value)
        
        t = tkns.get_next_token()
        self.assertEqual(tokeniser.TokenType.PATH_SEPARATOR, t.token_type)

        t = tkns.get_next_token()
        self.assertEqual(tokeniser.TokenType.WORD, t.token_type)
        self.assertEqual('ccc', t.value)
        
        t = tkns.get_next_token()
        self.assertEqual(tokeniser.TokenType.PATH_SEPARATOR, t.token_type)

        t = tkns.get_next_token()
        self.assertEqual(tokeniser.TokenType.WORD, t.token_type)
        self.assertEqual('ddd', t.value)
        
        t = tkns.get_next_token()
        self.assertEqual(None, t)
        
    def test_peek(self):
        
        tkns = Tokeniser(StringReader('aaa.bbb.ccc.ddd'))
        
        p = tkns.peek_next_token()
        self.assertNotEqual(None, p)
        self.assertEqual(tokeniser.TokenType.WORD, p.token_type)
        self.assertEqual('aaa', p.value)
        t = tkns.get_next_token()
        self.assertNotEqual(None, t)
        self.assertEqual(tokeniser.TokenType.WORD, t.token_type)
        self.assertEqual('aaa', t.value)
        
        p = tkns.peek_next_token()
        self.assertEqual(tokeniser.TokenType.PATH_SEPARATOR, p.token_type)
        t = tkns.get_next_token()
        self.assertEqual(tokeniser.TokenType.PATH_SEPARATOR, t.token_type)

        p = tkns.peek_next_token()
        self.assertEqual(tokeniser.TokenType.WORD, p.token_type)
        self.assertEqual('bbb', p.value)
        t = tkns.get_next_token()
        self.assertEqual(tokeniser.TokenType.WORD, t.token_type)
        self.assertEqual('bbb', t.value)
        
        p = tkns.peek_next_token()
        self.assertEqual(tokeniser.TokenType.PATH_SEPARATOR, p.token_type)
        t = tkns.get_next_token()
        self.assertEqual(tokeniser.TokenType.PATH_SEPARATOR, t.token_type)

        p = tkns.peek_next_token()
        self.assertEqual(tokeniser.TokenType.WORD, p.token_type)
        self.assertEqual('ccc', p.value)
        t = tkns.get_next_token()
        self.assertEqual(tokeniser.TokenType.WORD, t.token_type)
        self.assertEqual('ccc', t.value)
        
        p = tkns.peek_next_token()
        self.assertEqual(tokeniser.TokenType.PATH_SEPARATOR, p.token_type)
        t = tkns.get_next_token()
        self.assertEqual(tokeniser.TokenType.PATH_SEPARATOR, t.token_type)

        p = tkns.peek_next_token()
        self.assertEqual(tokeniser.TokenType.WORD, p.token_type)
        self.assertEqual('ddd', p.value)
        t = tkns.get_next_token()
        self.assertEqual(tokeniser.TokenType.WORD, t.token_type)
        self.assertEqual('ddd', t.value)
        
        p = tkns.peek_next_token()
        self.assertEqual(None, p)
        t = tkns.get_next_token()
        self.assertEqual(None, t)
        
    def test_root_path(self):
        
        tkns = Tokeniser(StringReader(':aaa.bbb.ccc.ddd'))
        
        t = tkns.get_next_token()
        self.assertNotEqual(None, t)
        self.assertEqual(tokeniser.TokenType.PATH_ROOT, t.token_type)

        t = tkns.get_next_token()
        self.assertEqual(tokeniser.TokenType.WORD, t.token_type)
        self.assertEqual('aaa', t.value)
        
        t = tkns.get_next_token()
        self.assertEqual(tokeniser.TokenType.PATH_SEPARATOR, t.token_type)

        t = tkns.get_next_token()
        self.assertEqual(tokeniser.TokenType.WORD, t.token_type)
        self.assertEqual('bbb', t.value)
        
        t = tkns.get_next_token()
        self.assertEqual(tokeniser.TokenType.PATH_SEPARATOR, t.token_type)

        t = tkns.get_next_token()
        self.assertEqual(tokeniser.TokenType.WORD, t.token_type)
        self.assertEqual('ccc', t.value)
        
        t = tkns.get_next_token()
        self.assertEqual(tokeniser.TokenType.PATH_SEPARATOR, t.token_type)

        t = tkns.get_next_token()
        self.assertEqual(tokeniser.TokenType.WORD, t.token_type)
        self.assertEqual('ddd', t.value)
        
        t = tkns.get_next_token()
        self.assertEqual(None, t)
        
    def test_not(self):
        
        tkns = Tokeniser(StringReader('!true'))
        
        t = tkns.get_next_token()
        self.assertNotEqual(None, t)
        self.assertEqual(tokeniser.TokenType.NOT, t.token_type)

        t = tkns.get_next_token()
        self.assertEqual(tokeniser.TokenType.LITERAL_BOOLEAN, t.token_type)
        self.assertEqual(True, t.value)
        
        t = tkns.get_next_token()
        self.assertEqual(None, t)
        
        
    def test_comparator(self):
        
        tkns = Tokeniser(StringReader(' aaa == bbb '))
        t = tkns.get_next_token()
        self.assertEqual(tokeniser.TokenType.WORD, t.token_type)
        self.assertEqual('aaa', t.value)
        
        t = tkns.get_next_token()
        self.assertEqual(tokeniser.TokenType.COMPARATOR_EQUAL, t.token_type)
        
        t = tkns.get_next_token()
        self.assertEqual(tokeniser.TokenType.WORD, t.token_type)
        self.assertEqual('bbb', t.value)
                
        t = tkns.get_next_token()
        self.assertEqual(None, t)
        
    def test_parameter(self):
        
        tkns = Tokeniser(StringReader(' aaa == $bbb '))
        t = tkns.get_next_token()
        self.assertEqual(tokeniser.TokenType.WORD, t.token_type)
        self.assertEqual('aaa', t.value)
        
        t = tkns.get_next_token()
        self.assertEqual(tokeniser.TokenType.COMPARATOR_EQUAL, t.token_type)
        
        t = tkns.get_next_token()
        self.assertEqual(tokeniser.TokenType.PARAMETER, t.token_type)
        self.assertEqual('bbb', t.value)
                
        t = tkns.get_next_token()
        self.assertEqual(None, t)
        
    def test_comparator_equals(self):
        tkns = Tokeniser(StringReader('aaa==bbb'))
        t = tkns.get_next_token()
        self.assertEqual(tokeniser.TokenType.WORD, t.token_type)
        self.assertEqual('aaa', t.value)
        
        t = tkns.get_next_token()
        self.assertEqual(tokeniser.TokenType.COMPARATOR_EQUAL, t.token_type)
        
        t = tkns.get_next_token()
        self.assertEqual(tokeniser.TokenType.WORD, t.token_type)
        self.assertEqual('bbb', t.value)
                
        t = tkns.get_next_token()
        self.assertEqual(None, t)
        
        tkns = Tokeniser(StringReader('aaa== bbb'))
        t = tkns.get_next_token()
        self.assertEqual(tokeniser.TokenType.WORD, t.token_type)
        self.assertEqual('aaa', t.value)
        
        t = tkns.get_next_token()
        self.assertEqual(tokeniser.TokenType.COMPARATOR_EQUAL, t.token_type)
        
        t = tkns.get_next_token()
        self.assertEqual(tokeniser.TokenType.WORD, t.token_type)
        self.assertEqual('bbb', t.value)
                
        t = tkns.get_next_token()
        self.assertEqual(None, t)
        
        tkns = Tokeniser(StringReader('aaa ==bbb'))
        t = tkns.get_next_token()
        self.assertEqual(tokeniser.TokenType.WORD, t.token_type)
        self.assertEqual('aaa', t.value)
        
        t = tkns.get_next_token()
        self.assertEqual(tokeniser.TokenType.COMPARATOR_EQUAL, t.token_type)
        
        t = tkns.get_next_token()
        self.assertEqual(tokeniser.TokenType.WORD, t.token_type)
        self.assertEqual('bbb', t.value)
                
        t = tkns.get_next_token()
        self.assertEqual(None, t)
        
        tkns = Tokeniser(StringReader('aaa == bbb'))
        t = tkns.get_next_token()
        self.assertEqual(tokeniser.TokenType.WORD, t.token_type)
        self.assertEqual('aaa', t.value)
        
        t = tkns.get_next_token()
        self.assertEqual(tokeniser.TokenType.COMPARATOR_EQUAL, t.token_type)
        
        t = tkns.get_next_token()
        self.assertEqual(tokeniser.TokenType.WORD, t.token_type)
        self.assertEqual('bbb', t.value)
                
        t = tkns.get_next_token()
        self.assertEqual(None, t)
        
    def test_comparator_not_equals(self):
        tkns = Tokeniser(StringReader('aaa!=bbb'))
        t = tkns.get_next_token()
        self.assertEqual(tokeniser.TokenType.WORD, t.token_type)
        self.assertEqual('aaa', t.value)
        
        t = tkns.get_next_token()
        self.assertEqual(tokeniser.TokenType.COMPARATOR_NE, t.token_type)
        
        t = tkns.get_next_token()
        self.assertEqual(tokeniser.TokenType.WORD, t.token_type)
        self.assertEqual('bbb', t.value)
                
        t = tkns.get_next_token()
        self.assertEqual(None, t)
        
        tkns = Tokeniser(StringReader('aaa!= bbb'))
        t = tkns.get_next_token()
        self.assertEqual(tokeniser.TokenType.WORD, t.token_type)
        self.assertEqual('aaa', t.value)
        
        t = tkns.get_next_token()
        self.assertEqual(tokeniser.TokenType.COMPARATOR_NE, t.token_type)
        
        t = tkns.get_next_token()
        self.assertEqual(tokeniser.TokenType.WORD, t.token_type)
        self.assertEqual('bbb', t.value)
                
        t = tkns.get_next_token()
        self.assertEqual(None, t)
        
        tkns = Tokeniser(StringReader('aaa !=bbb'))
        t = tkns.get_next_token()
        self.assertEqual(tokeniser.TokenType.WORD, t.token_type)
        self.assertEqual('aaa', t.value)
        
        t = tkns.get_next_token()
        self.assertEqual(tokeniser.TokenType.COMPARATOR_NE, t.token_type)
        
        t = tkns.get_next_token()
        self.assertEqual(tokeniser.TokenType.WORD, t.token_type)
        self.assertEqual('bbb', t.value)
                
        t = tkns.get_next_token()
        self.assertEqual(None, t)
        
        tkns = Tokeniser(StringReader('aaa != bbb'))
        t = tkns.get_next_token()
        self.assertEqual(tokeniser.TokenType.WORD, t.token_type)
        self.assertEqual('aaa', t.value)
        
        t = tkns.get_next_token()
        self.assertEqual(tokeniser.TokenType.COMPARATOR_NE, t.token_type)
        
        t = tkns.get_next_token()
        self.assertEqual(tokeniser.TokenType.WORD, t.token_type)
        self.assertEqual('bbb', t.value)
                
        t = tkns.get_next_token()
        self.assertEqual(None, t)
        
    def test_comparator_greater_than(self):
        tkns = Tokeniser(StringReader('aaa>bbb'))
        t = tkns.get_next_token()
        self.assertEqual(tokeniser.TokenType.WORD, t.token_type)
        self.assertEqual('aaa', t.value)
        
        t = tkns.get_next_token()
        self.assertEqual(tokeniser.TokenType.COMPARATOR_GT, t.token_type)
        
        t = tkns.get_next_token()
        self.assertEqual(tokeniser.TokenType.WORD, t.token_type)
        self.assertEqual('bbb', t.value)
                
        t = tkns.get_next_token()
        self.assertEqual(None, t)
        
        tkns = Tokeniser(StringReader('aaa >bbb'))
        t = tkns.get_next_token()
        self.assertEqual(tokeniser.TokenType.WORD, t.token_type)
        self.assertEqual('aaa', t.value)
        
        t = tkns.get_next_token()
        self.assertEqual(tokeniser.TokenType.COMPARATOR_GT, t.token_type)
        
        t = tkns.get_next_token()
        self.assertEqual(tokeniser.TokenType.WORD, t.token_type)
        self.assertEqual('bbb', t.value)
                
        t = tkns.get_next_token()
        self.assertEqual(None, t)
        
        tkns = Tokeniser(StringReader('aaa> bbb'))
        t = tkns.get_next_token()
        self.assertEqual(tokeniser.TokenType.WORD, t.token_type)
        self.assertEqual('aaa', t.value)
        
        t = tkns.get_next_token()
        self.assertEqual(tokeniser.TokenType.COMPARATOR_GT, t.token_type)
        
        t = tkns.get_next_token()
        self.assertEqual(tokeniser.TokenType.WORD, t.token_type)
        self.assertEqual('bbb', t.value)
                
        t = tkns.get_next_token()
        self.assertEqual(None, t)

        tkns = Tokeniser(StringReader('aaa > bbb'))
        t = tkns.get_next_token()
        self.assertEqual(tokeniser.TokenType.WORD, t.token_type)
        self.assertEqual('aaa', t.value)
        
        t = tkns.get_next_token()
        self.assertEqual(tokeniser.TokenType.COMPARATOR_GT, t.token_type)
        
        t = tkns.get_next_token()
        self.assertEqual(tokeniser.TokenType.WORD, t.token_type)
        self.assertEqual('bbb', t.value)
                
        t = tkns.get_next_token()
        self.assertEqual(None, t)
        
    def test_comparator_greater_than_or_equal(self):
        tkns = Tokeniser(StringReader('aaa>=bbb'))
        t = tkns.get_next_token()
        self.assertEqual(tokeniser.TokenType.WORD, t.token_type)
        self.assertEqual('aaa', t.value)
        
        t = tkns.get_next_token()
        self.assertEqual(tokeniser.TokenType.COMPARATOR_GE, t.token_type)
        
        t = tkns.get_next_token()
        self.assertEqual(tokeniser.TokenType.WORD, t.token_type)
        self.assertEqual('bbb', t.value)
                
        t = tkns.get_next_token()
        self.assertEqual(None, t)
        
        tkns = Tokeniser(StringReader('aaa >=bbb'))
        t = tkns.get_next_token()
        self.assertEqual(tokeniser.TokenType.WORD, t.token_type)
        self.assertEqual('aaa', t.value)
        
        t = tkns.get_next_token()
        self.assertEqual(tokeniser.TokenType.COMPARATOR_GE, t.token_type)
        
        t = tkns.get_next_token()
        self.assertEqual(tokeniser.TokenType.WORD, t.token_type)
        self.assertEqual('bbb', t.value)
                
        t = tkns.get_next_token()
        self.assertEqual(None, t)
        
        tkns = Tokeniser(StringReader('aaa>= bbb'))
        t = tkns.get_next_token()
        self.assertEqual(tokeniser.TokenType.WORD, t.token_type)
        self.assertEqual('aaa', t.value)
        
        t = tkns.get_next_token()
        self.assertEqual(tokeniser.TokenType.COMPARATOR_GE, t.token_type)
        
        t = tkns.get_next_token()
        self.assertEqual(tokeniser.TokenType.WORD, t.token_type)
        self.assertEqual('bbb', t.value)
                
        t = tkns.get_next_token()
        self.assertEqual(None, t)

        tkns = Tokeniser(StringReader('aaa >= bbb'))
        t = tkns.get_next_token()
        self.assertEqual(tokeniser.TokenType.WORD, t.token_type)
        self.assertEqual('aaa', t.value)
        
        t = tkns.get_next_token()
        self.assertEqual(tokeniser.TokenType.COMPARATOR_GE, t.token_type)
        
        t = tkns.get_next_token()
        self.assertEqual(tokeniser.TokenType.WORD, t.token_type)
        self.assertEqual('bbb', t.value)
                
        t = tkns.get_next_token()
        self.assertEqual(None, t)
        
    def test_comparator_less_than(self):
        tkns = Tokeniser(StringReader('aaa<bbb'))
        t = tkns.get_next_token()
        self.assertEqual(tokeniser.TokenType.WORD, t.token_type)
        self.assertEqual('aaa', t.value)
        
        t = tkns.get_next_token()
        self.assertEqual(tokeniser.TokenType.COMPARATOR_LT, t.token_type)
        
        t = tkns.get_next_token()
        self.assertEqual(tokeniser.TokenType.WORD, t.token_type)
        self.assertEqual('bbb', t.value)
                
        t = tkns.get_next_token()
        self.assertEqual(None, t)
        
        tkns = Tokeniser(StringReader('aaa <bbb'))
        t = tkns.get_next_token()
        self.assertEqual(tokeniser.TokenType.WORD, t.token_type)
        self.assertEqual('aaa', t.value)
        
        t = tkns.get_next_token()
        self.assertEqual(tokeniser.TokenType.COMPARATOR_LT, t.token_type)
        
        t = tkns.get_next_token()
        self.assertEqual(tokeniser.TokenType.WORD, t.token_type)
        self.assertEqual('bbb', t.value)
                
        t = tkns.get_next_token()
        self.assertEqual(None, t)
        
        tkns = Tokeniser(StringReader('aaa< bbb'))
        t = tkns.get_next_token()
        self.assertEqual(tokeniser.TokenType.WORD, t.token_type)
        self.assertEqual('aaa', t.value)
        
        t = tkns.get_next_token()
        self.assertEqual(tokeniser.TokenType.COMPARATOR_LT, t.token_type)
        
        t = tkns.get_next_token()
        self.assertEqual(tokeniser.TokenType.WORD, t.token_type)
        self.assertEqual('bbb', t.value)
                
        t = tkns.get_next_token()
        self.assertEqual(None, t)

        tkns = Tokeniser(StringReader('aaa < bbb'))
        t = tkns.get_next_token()
        self.assertEqual(tokeniser.TokenType.WORD, t.token_type)
        self.assertEqual('aaa', t.value)
        
        t = tkns.get_next_token()
        self.assertEqual(tokeniser.TokenType.COMPARATOR_LT, t.token_type)
        
        t = tkns.get_next_token()
        self.assertEqual(tokeniser.TokenType.WORD, t.token_type)
        self.assertEqual('bbb', t.value)
                
        t = tkns.get_next_token()
        self.assertEqual(None, t)
        
    def test_comparator_less_than_or_equal(self):
        tkns = Tokeniser(StringReader('aaa<=bbb'))
        t = tkns.get_next_token()
        self.assertEqual(tokeniser.TokenType.WORD, t.token_type)
        self.assertEqual('aaa', t.value)
        
        t = tkns.get_next_token()
        self.assertEqual(tokeniser.TokenType.COMPARATOR_LE, t.token_type)
        
        t = tkns.get_next_token()
        self.assertEqual(tokeniser.TokenType.WORD, t.token_type)
        self.assertEqual('bbb', t.value)
                
        t = tkns.get_next_token()
        self.assertEqual(None, t)
        
        tkns = Tokeniser(StringReader('aaa <=bbb'))
        t = tkns.get_next_token()
        self.assertEqual(tokeniser.TokenType.WORD, t.token_type)
        self.assertEqual('aaa', t.value)
        
        t = tkns.get_next_token()
        self.assertEqual(tokeniser.TokenType.COMPARATOR_LE, t.token_type)
        
        t = tkns.get_next_token()
        self.assertEqual(tokeniser.TokenType.WORD, t.token_type)
        self.assertEqual('bbb', t.value)
                
        t = tkns.get_next_token()
        self.assertEqual(None, t)
        
        tkns = Tokeniser(StringReader('aaa<= bbb'))
        t = tkns.get_next_token()
        self.assertEqual(tokeniser.TokenType.WORD, t.token_type)
        self.assertEqual('aaa', t.value)
        
        t = tkns.get_next_token()
        self.assertEqual(tokeniser.TokenType.COMPARATOR_LE, t.token_type)
        
        t = tkns.get_next_token()
        self.assertEqual(tokeniser.TokenType.WORD, t.token_type)
        self.assertEqual('bbb', t.value)
                
        t = tkns.get_next_token()
        self.assertEqual(None, t)

        tkns = Tokeniser(StringReader('aaa <= bbb'))
        t = tkns.get_next_token()
        self.assertEqual(tokeniser.TokenType.WORD, t.token_type)
        self.assertEqual('aaa', t.value)
        
        t = tkns.get_next_token()
        self.assertEqual(tokeniser.TokenType.COMPARATOR_LE, t.token_type)
        
        t = tkns.get_next_token()
        self.assertEqual(tokeniser.TokenType.WORD, t.token_type)
        self.assertEqual('bbb', t.value)
                
        t = tkns.get_next_token()
        self.assertEqual(None, t)
        
    def test_plus(self):
        tkns = Tokeniser(StringReader('aaa+bbb'))
        t = tkns.get_next_token()
        self.assertEqual(tokeniser.TokenType.WORD, t.token_type)
        self.assertEqual('aaa', t.value)
        
        t = tkns.get_next_token()
        self.assertEqual(tokeniser.TokenType.OPERATOR_PLUS, t.token_type)
        
        t = tkns.get_next_token()
        self.assertEqual(tokeniser.TokenType.WORD, t.token_type)
        self.assertEqual('bbb', t.value)
                
        t = tkns.get_next_token()
        self.assertEqual(None, t)
        
        tkns = Tokeniser(StringReader('aaa +bbb'))
        t = tkns.get_next_token()
        self.assertEqual(tokeniser.TokenType.WORD, t.token_type)
        self.assertEqual('aaa', t.value)
        
        t = tkns.get_next_token()
        self.assertEqual(tokeniser.TokenType.OPERATOR_PLUS, t.token_type)
        
        t = tkns.get_next_token()
        self.assertEqual(tokeniser.TokenType.WORD, t.token_type)
        self.assertEqual('bbb', t.value)
                
        t = tkns.get_next_token()
        self.assertEqual(None, t)
        
        tkns = Tokeniser(StringReader('aaa+ bbb'))
        t = tkns.get_next_token()
        self.assertEqual(tokeniser.TokenType.WORD, t.token_type)
        self.assertEqual('aaa', t.value)
        
        t = tkns.get_next_token()
        self.assertEqual(tokeniser.TokenType.OPERATOR_PLUS, t.token_type)
        
        t = tkns.get_next_token()
        self.assertEqual(tokeniser.TokenType.WORD, t.token_type)
        self.assertEqual('bbb', t.value)
                
        t = tkns.get_next_token()
        self.assertEqual(None, t)

        tkns = Tokeniser(StringReader('aaa + bbb'))
        t = tkns.get_next_token()
        self.assertEqual(tokeniser.TokenType.WORD, t.token_type)
        self.assertEqual('aaa', t.value)
        
        t = tkns.get_next_token()
        self.assertEqual(tokeniser.TokenType.OPERATOR_PLUS, t.token_type)
        
        t = tkns.get_next_token()
        self.assertEqual(tokeniser.TokenType.WORD, t.token_type)
        self.assertEqual('bbb', t.value)
                
        t = tkns.get_next_token()
        self.assertEqual(None, t)
        
    def test_minus(self):
        tkns = Tokeniser(StringReader('aaa-bbb'))
        t = tkns.get_next_token()
        self.assertEqual(tokeniser.TokenType.WORD, t.token_type)
        self.assertEqual('aaa', t.value)
        
        t = tkns.get_next_token()
        self.assertEqual(tokeniser.TokenType.OPERATOR_MINUS, t.token_type)
        
        t = tkns.get_next_token()
        self.assertEqual(tokeniser.TokenType.WORD, t.token_type)
        self.assertEqual('bbb', t.value)
                
        t = tkns.get_next_token()
        self.assertEqual(None, t)
        
        tkns = Tokeniser(StringReader('aaa -bbb'))
        t = tkns.get_next_token()
        self.assertEqual(tokeniser.TokenType.WORD, t.token_type)
        self.assertEqual('aaa', t.value)
        
        t = tkns.get_next_token()
        self.assertEqual(tokeniser.TokenType.OPERATOR_MINUS, t.token_type)
        
        t = tkns.get_next_token()
        self.assertEqual(tokeniser.TokenType.WORD, t.token_type)
        self.assertEqual('bbb', t.value)
                
        t = tkns.get_next_token()
        self.assertEqual(None, t)
        
        tkns = Tokeniser(StringReader('aaa- bbb'))
        t = tkns.get_next_token()
        self.assertEqual(tokeniser.TokenType.WORD, t.token_type)
        self.assertEqual('aaa', t.value)
        
        t = tkns.get_next_token()
        self.assertEqual(tokeniser.TokenType.OPERATOR_MINUS, t.token_type)
        
        t = tkns.get_next_token()
        self.assertEqual(tokeniser.TokenType.WORD, t.token_type)
        self.assertEqual('bbb', t.value)
                
        t = tkns.get_next_token()
        self.assertEqual(None, t)

        tkns = Tokeniser(StringReader('aaa - bbb'))
        t = tkns.get_next_token()
        self.assertEqual(tokeniser.TokenType.WORD, t.token_type)
        self.assertEqual('aaa', t.value)
        
        t = tkns.get_next_token()
        self.assertEqual(tokeniser.TokenType.OPERATOR_MINUS, t.token_type)
        
        t = tkns.get_next_token()
        self.assertEqual(tokeniser.TokenType.WORD, t.token_type)
        self.assertEqual('bbb', t.value)
                
        t = tkns.get_next_token()
        self.assertEqual(None, t)
        
    def test_multiply(self):
        tkns = Tokeniser(StringReader('aaa*bbb'))
        t = tkns.get_next_token()
        self.assertEqual(tokeniser.TokenType.WORD, t.token_type)
        self.assertEqual('aaa', t.value)
        
        t = tkns.get_next_token()
        self.assertEqual(tokeniser.TokenType.OPERATOR_MULTIPLY, t.token_type)
        
        t = tkns.get_next_token()
        self.assertEqual(tokeniser.TokenType.WORD, t.token_type)
        self.assertEqual('bbb', t.value)
                
        t = tkns.get_next_token()
        self.assertEqual(None, t)
        
        tkns = Tokeniser(StringReader('aaa *bbb'))
        t = tkns.get_next_token()
        self.assertEqual(tokeniser.TokenType.WORD, t.token_type)
        self.assertEqual('aaa', t.value)
        
        t = tkns.get_next_token()
        self.assertEqual(tokeniser.TokenType.OPERATOR_MULTIPLY, t.token_type)
        
        t = tkns.get_next_token()
        self.assertEqual(tokeniser.TokenType.WORD, t.token_type)
        self.assertEqual('bbb', t.value)
                
        t = tkns.get_next_token()
        self.assertEqual(None, t)
        
        tkns = Tokeniser(StringReader('aaa* bbb'))
        t = tkns.get_next_token()
        self.assertEqual(tokeniser.TokenType.WORD, t.token_type)
        self.assertEqual('aaa', t.value)
        
        t = tkns.get_next_token()
        self.assertEqual(tokeniser.TokenType.OPERATOR_MULTIPLY, t.token_type)
        
        t = tkns.get_next_token()
        self.assertEqual(tokeniser.TokenType.WORD, t.token_type)
        self.assertEqual('bbb', t.value)
                
        t = tkns.get_next_token()
        self.assertEqual(None, t)

        tkns = Tokeniser(StringReader('aaa * bbb'))
        t = tkns.get_next_token()
        self.assertEqual(tokeniser.TokenType.WORD, t.token_type)
        self.assertEqual('aaa', t.value)
        
        t = tkns.get_next_token()
        self.assertEqual(tokeniser.TokenType.OPERATOR_MULTIPLY, t.token_type)
        
        t = tkns.get_next_token()
        self.assertEqual(tokeniser.TokenType.WORD, t.token_type)
        self.assertEqual('bbb', t.value)
                
        t = tkns.get_next_token()
        self.assertEqual(None, t)
        
    def test_divide(self):
        tkns = Tokeniser(StringReader('aaa/bbb'))
        t = tkns.get_next_token()
        self.assertEqual(tokeniser.TokenType.WORD, t.token_type)
        self.assertEqual('aaa', t.value)
        
        t = tkns.get_next_token()
        self.assertEqual(tokeniser.TokenType.OPERATOR_DIVIDE, t.token_type)
        
        t = tkns.get_next_token()
        self.assertEqual(tokeniser.TokenType.WORD, t.token_type)
        self.assertEqual('bbb', t.value)
                
        t = tkns.get_next_token()
        self.assertEqual(None, t)
        
        tkns = Tokeniser(StringReader('aaa /bbb'))
        t = tkns.get_next_token()
        self.assertEqual(tokeniser.TokenType.WORD, t.token_type)
        self.assertEqual('aaa', t.value)
        
        t = tkns.get_next_token()
        self.assertEqual(tokeniser.TokenType.OPERATOR_DIVIDE, t.token_type)
        
        t = tkns.get_next_token()
        self.assertEqual(tokeniser.TokenType.WORD, t.token_type)
        self.assertEqual('bbb', t.value)
                
        t = tkns.get_next_token()
        self.assertEqual(None, t)
        
        tkns = Tokeniser(StringReader('aaa/ bbb'))
        t = tkns.get_next_token()
        self.assertEqual(tokeniser.TokenType.WORD, t.token_type)
        self.assertEqual('aaa', t.value)
        
        t = tkns.get_next_token()
        self.assertEqual(tokeniser.TokenType.OPERATOR_DIVIDE, t.token_type)
        
        t = tkns.get_next_token()
        self.assertEqual(tokeniser.TokenType.WORD, t.token_type)
        self.assertEqual('bbb', t.value)
                
        t = tkns.get_next_token()
        self.assertEqual(None, t)

        tkns = Tokeniser(StringReader('aaa / bbb'))
        t = tkns.get_next_token()
        self.assertEqual(tokeniser.TokenType.WORD, t.token_type)
        self.assertEqual('aaa', t.value)
        
        t = tkns.get_next_token()
        self.assertEqual(tokeniser.TokenType.OPERATOR_DIVIDE, t.token_type)
        
        t = tkns.get_next_token()
        self.assertEqual(tokeniser.TokenType.WORD, t.token_type)
        self.assertEqual('bbb', t.value)
                
        t = tkns.get_next_token()
        self.assertEqual(None, t)
        
    def test_group(self):
        tkns = Tokeniser(StringReader('aaa(bbb,ccc,ddd)'))
        t = tkns.get_next_token()
        self.assertEqual(tokeniser.TokenType.WORD, t.token_type)
        self.assertEqual('aaa', t.value)
        
        t = tkns.get_next_token()
        self.assertEqual(tokeniser.TokenType.START_GROUP, t.token_type)
        
        t = tkns.get_next_token()
        self.assertEqual(tokeniser.TokenType.WORD, t.token_type)
        self.assertEqual('bbb', t.value)
                
        t = tkns.get_next_token()
        self.assertEqual(tokeniser.TokenType.GROUP_SEPARATOR, t.token_type)
        
        t = tkns.get_next_token()
        self.assertEqual(tokeniser.TokenType.WORD, t.token_type)
        self.assertEqual('ccc', t.value)
                
        t = tkns.get_next_token()
        self.assertEqual(tokeniser.TokenType.GROUP_SEPARATOR, t.token_type)
        
        t = tkns.get_next_token()
        self.assertEqual(tokeniser.TokenType.WORD, t.token_type)
        self.assertEqual('ddd', t.value)
                
        t = tkns.get_next_token()
        self.assertEqual(tokeniser.TokenType.END_GROUP, t.token_type)
        
        t = tkns.get_next_token()
        self.assertEqual(None, t)
        
        tkns = Tokeniser(StringReader(' aaa ( bbb , ccc , ddd ) '))
        t = tkns.get_next_token()
        self.assertEqual(tokeniser.TokenType.WORD, t.token_type)
        self.assertEqual('aaa', t.value)
        
        t = tkns.get_next_token()
        self.assertEqual(tokeniser.TokenType.START_GROUP, t.token_type)
        
        t = tkns.get_next_token()
        self.assertEqual(tokeniser.TokenType.WORD, t.token_type)
        self.assertEqual('bbb', t.value)
                
        t = tkns.get_next_token()
        self.assertEqual(tokeniser.TokenType.GROUP_SEPARATOR, t.token_type)
        
        t = tkns.get_next_token()
        self.assertEqual(tokeniser.TokenType.WORD, t.token_type)
        self.assertEqual('ccc', t.value)
                
        t = tkns.get_next_token()
        self.assertEqual(tokeniser.TokenType.GROUP_SEPARATOR, t.token_type)
        
        t = tkns.get_next_token()
        self.assertEqual(tokeniser.TokenType.WORD, t.token_type)
        self.assertEqual('ddd', t.value)
                
        t = tkns.get_next_token()
        self.assertEqual(tokeniser.TokenType.END_GROUP, t.token_type)
        
        t = tkns.get_next_token()
        self.assertEqual(None, t)
        
    def test_filter(self):
        tkns = Tokeniser(StringReader('aaa[bbb==123&ccc!="xyz"]'))
        t = tkns.get_next_token()
        self.assertEqual(tokeniser.TokenType.WORD, t.token_type)
        self.assertEqual('aaa', t.value)
        
        t = tkns.get_next_token()
        self.assertEqual(tokeniser.TokenType.START_FILTER, t.token_type)
        
        t = tkns.get_next_token()
        self.assertEqual(tokeniser.TokenType.WORD, t.token_type)
        self.assertEqual('bbb', t.value)
                
        t = tkns.get_next_token()
        self.assertEqual(tokeniser.TokenType.COMPARATOR_EQUAL, t.token_type)
        
        t = tkns.get_next_token()
        self.assertEqual(tokeniser.TokenType.LITERAL_INT, t.token_type)
        self.assertEqual(123, t.value)
                
        t = tkns.get_next_token()
        self.assertEqual(tokeniser.TokenType.AND_SEPARATOR, t.token_type)
        
        t = tkns.get_next_token()
        self.assertEqual(tokeniser.TokenType.WORD, t.token_type)
        self.assertEqual('ccc', t.value)
                
        t = tkns.get_next_token()
        self.assertEqual(tokeniser.TokenType.COMPARATOR_NE, t.token_type)
        
        t = tkns.get_next_token()
        self.assertEqual(tokeniser.TokenType.LITERAL_STRING, t.token_type)
        self.assertEqual('xyz', t.value)
                
        t = tkns.get_next_token()
        self.assertEqual(tokeniser.TokenType.END_FILTER, t.token_type)
        
        t = tkns.get_next_token()
        self.assertEqual(None, t)
        
        tkns = Tokeniser(StringReader(' aaa [ bbb == 123 & ccc != "xyz" ] '))
        t = tkns.get_next_token()
        self.assertEqual(tokeniser.TokenType.WORD, t.token_type)
        self.assertEqual('aaa', t.value)
        
        t = tkns.get_next_token()
        self.assertEqual(tokeniser.TokenType.START_FILTER, t.token_type)
        
        t = tkns.get_next_token()
        self.assertEqual(tokeniser.TokenType.WORD, t.token_type)
        self.assertEqual('bbb', t.value)
                
        t = tkns.get_next_token()
        self.assertEqual(tokeniser.TokenType.COMPARATOR_EQUAL, t.token_type)
        
        t = tkns.get_next_token()
        self.assertEqual(tokeniser.TokenType.LITERAL_INT, t.token_type)
        self.assertEqual(123, t.value)
                
        t = tkns.get_next_token()
        self.assertEqual(tokeniser.TokenType.AND_SEPARATOR, t.token_type)
        
        t = tkns.get_next_token()
        self.assertEqual(tokeniser.TokenType.WORD, t.token_type)
        self.assertEqual('ccc', t.value)
                
        t = tkns.get_next_token()
        self.assertEqual(tokeniser.TokenType.COMPARATOR_NE, t.token_type)
        
        t = tkns.get_next_token()
        self.assertEqual(tokeniser.TokenType.LITERAL_STRING, t.token_type)
        self.assertEqual('xyz', t.value)
                
        t = tkns.get_next_token()
        self.assertEqual(tokeniser.TokenType.END_FILTER, t.token_type)
        
        t = tkns.get_next_token()
        self.assertEqual(None, t)
        
    def test_literal_string(self):
        tkns = Tokeniser(StringReader('"abc", "abc\\n\\t\\b\\"xyz"' ))
        t = tkns.get_next_token()
        self.assertEqual(tokeniser.TokenType.LITERAL_STRING, t.token_type)
        self.assertEqual('abc', t.value)
        
        t = tkns.get_next_token()
        self.assertEqual(tokeniser.TokenType.GROUP_SEPARATOR, t.token_type)
        
        t = tkns.get_next_token()
        self.assertEqual(tokeniser.TokenType.LITERAL_STRING, t.token_type)
        self.assertEqual('abc\n\t\b"xyz', t.value)
                
        
        t = tkns.get_next_token()
        self.assertEqual(None, t)
        
    def test_literal_number(self):
        tkns = Tokeniser(StringReader('123, 123.456' ))
        t = tkns.get_next_token()
        self.assertEqual(tokeniser.TokenType.LITERAL_INT, t.token_type)
        self.assertEqual(123, t.value)
        
        t = tkns.get_next_token()
        self.assertEqual(tokeniser.TokenType.GROUP_SEPARATOR, t.token_type)
        
        t = tkns.get_next_token()
        self.assertEqual(tokeniser.TokenType.LITERAL_FLOAT, t.token_type)
        self.assertEqual(123.456, t.value)
                
        
        t = tkns.get_next_token()
        self.assertEqual(None, t)
        
    def test_literal_boolean(self):
        tkns = Tokeniser(StringReader('true, false' ))
        t = tkns.get_next_token()
        self.assertEqual(tokeniser.TokenType.LITERAL_BOOLEAN, t.token_type)
        self.assertEqual(True, t.value)
        
        t = tkns.get_next_token()
        self.assertEqual(tokeniser.TokenType.GROUP_SEPARATOR, t.token_type)
        
        t = tkns.get_next_token()
        self.assertEqual(tokeniser.TokenType.LITERAL_BOOLEAN, t.token_type)
        self.assertEqual(False, t.value)
                
        
        t = tkns.get_next_token()
        self.assertEqual(None, t)
        
        
        
        
        


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()