'''
Created on 28 Dec 2018

@author: simon
'''
import unittest
from utilities.readers import StringReader
from expressions.pypath import ExpressionParser
from expressions.pypath.tokeniser import Tokeniser
from expressions import *

import logging, logging.config
NO_LOG = 9999999
LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'detailed': {'class': 'logging.Formatter', 'format': '%(levelname)-8s %(name)-35s %(funcName)-30s line:%(lineno)5d %(message)s'}
    },
    'handlers': {
        'console': {'class': 'logging.StreamHandler', 'formatter': 'detailed'}
    },
    'loggers': {
        'root':                            {'level': 'WARN',   'handlers': ['console']},
        'expressions':                     {'level': 'WARN',   'handlers': ['console']},
        'expressions.pypath':              {'level': NO_LOG,  'handlers': ['console'], 'propagate': False},
        'expressions.pypath.tokeniser':    {'level': NO_LOG,  'handlers': ['console'], 'propagate': False}
    }
}
logging.config.dictConfig(LOGGING)

class TestPyPath(unittest.TestCase):

    def test_new_parser(self):
        p = ExpressionParser(Tokeniser(StringReader('aaa.bbb.ccc')))
        self.assertNotEqual(None, p)

    def test_parse_field(self):
        p = ExpressionParser(Tokeniser(StringReader('aaa')))
        exp = p.get_expression()
        self.assertEqual('aaa', exp.field)

    def test_parse_path(self):
        p = ExpressionParser(Tokeniser(StringReader('aaa.bbb.ccc')))
        exp = p.get_expression()
        self.assertNotEqual(None, exp)
        self.assertTrue(isinstance(exp, Path))
        self.assertEqual('ccc', exp.field)
        self.assertTrue(isinstance(exp.path, Path))
        self.assertEqual('bbb', exp.path.field)
        self.assertTrue(isinstance(exp.path.path, Field))
        self.assertEqual('aaa', exp.path.path.field)
        
    def test_parse_equals(self):
        p = ExpressionParser(Tokeniser(StringReader('aaa == bbb')))
        exp = p.get_expression()
        self.assertNotEqual(None, exp)
        self.assertTrue(isinstance(exp, Equals))
        self.assertTrue(isinstance(exp.lhs, Field))
        self.assertEqual('aaa', exp.lhs.field)
        self.assertTrue(isinstance(exp.rhs, Field))
        self.assertEqual('bbb', exp.rhs.field)
        
    def test_parse_filter_in_path(self):
        p = ExpressionParser(Tokeniser(StringReader('aaa.bbb[ccc>123].ddd')))
        expr = p.get_expression()
        
        print(expr.to_path())
        
        self.assertTrue(isinstance(expr, Path))
        self.assertEqual('ddd', expr.field)
        self.assertEqual(None, expr.list_index)
        self.assertEqual(None, expr.list_filter)
        self.assertTrue(isinstance(expr.path, Path))
        self.assertEqual('bbb', expr.path.field)
        self.assertEqual(None, expr.path.list_index)
        self.assertNotEqual(None, expr.path.list_filter)
        self.assertTrue(isinstance(expr.path.list_filter, Filter))
        self.assertTrue(isinstance(expr.path.list_filter.filter, GreaterThan))
        self.assertTrue(isinstance(expr.path.list_filter.filter.lhs, Field))
        self.assertEqual('ccc', expr.path.list_filter.filter.lhs.field)
        self.assertTrue(isinstance(expr.path.list_filter.filter.rhs, Literal))
        self.assertEqual(123, expr.path.list_filter.filter.rhs.literal)
        self.assertTrue(isinstance(expr.path.path, Field))
        self.assertEqual('aaa', expr.path.path.field)
        self.assertEqual(None, expr.path.path.list_index)
        self.assertEqual(None, expr.path.path.list_filter)
        
    def test_parse_or(self):
        p = ExpressionParser(Tokeniser(StringReader('(True|False)')))
        exp = p.get_expression()
        self.assertNotEqual(None, exp)
        self.assertTrue(isinstance(exp, Or))
        self.assertEqual(2, len(exp.items))
        self.assertTrue(isinstance(exp.items[0], Literal))
        self.assertEqual(True, exp.items[0].literal)
        self.assertTrue(isinstance(exp.items[1], Literal))
        self.assertEqual(False, exp.items[1].literal)
        

        
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()