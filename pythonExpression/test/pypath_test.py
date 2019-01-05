'''
Created on 28 Dec 2018

@author: simon
'''
import unittest
from utilities.readers import StringReader
from expressions.pypath import *
from expressions.pypath.tokeniser import *


class TestPyPath(unittest.TestCase):

    def test_new_parser(self):
        p = ExpressionParser(Tokeniser(StringReader('aaa.bbb.ccc')))
        self.assertNotEqual(None, p)

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
        
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()