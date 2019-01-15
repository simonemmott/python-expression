'''
Created on 28 Dec 2018

@author: simon
'''
import unittest
from test_entities import *
from expressions import *
from utilities.readers import StringReader
from utilities import classUtil
from expressions.pypath import *
from expressions.pypath.tokeniser import *
import json

import logging, logging.config
NO_LOG = 9999999
LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'detailed': {'class': 'logging.Formatter', 'format': '%(levelname)-8s %(name)-35s %(funcName)-30s line: %(lineno)5d %(message)s'}
    },
    'handlers': {
        'console': {'class': 'logging.StreamHandler', 'formatter': 'detailed'}
    },
    'loggers': {
        'root':                            {'level': 'INFO',   'handlers': ['console']},
        'expressions':                     {'level': 'DEBUG',  'handlers': ['console'], 'propagate': False},
        'expressions.pypath':              {'level': NO_LOG,  'handlers': ['console'], 'propagate': False}
    }
}
logging.config.dictConfig(LOGGING)

Q = TokenType.QUOTE.value

class TestField(unittest.TestCase):

    def test_evaluate(self):
        eA_1 = EntityA(id=1, name='EA_1', description='This is EA 1')
        eA_2 = EntityA(id=2, name='EA_2', description='This is EA 2')
        eC_1 = EntityC(id=1, name='EC_1', description='This is EC 1')
        eC_2 = EntityC(id=2, name='EC_2', description='This is EC 2')
        
        id_field = Field('id')
        name_field = Field('name')
        description_field = Field('description')
        
        self.assertEqual(1, id_field.evaluate(eA_1))
        self.assertEqual(2, id_field.evaluate(eA_2))
        self.assertEqual(1, id_field.evaluate(eC_1))
        self.assertEqual(2, id_field.evaluate(eC_2))
        
        self.assertEqual('EA_1', name_field.evaluate(eA_1))
        self.assertEqual('EA_2', name_field.evaluate(eA_2))
        self.assertEqual('EC_1', name_field.evaluate(eC_1))
        self.assertEqual('EC_2', name_field.evaluate(eC_2))
        
        self.assertEqual('This is EA 1', description_field.evaluate(eA_1))
        self.assertEqual('This is EA 2', description_field.evaluate(eA_2))
        self.assertEqual('This is EC 1', description_field.evaluate(eC_1))
        self.assertEqual('This is EC 2', description_field.evaluate(eC_2))
        
    def test_evaluate_filter(self):
        
        root = RootEntity(id=1, name='root_1')
        parent1 = ParentEntity(id=1, name='parent_1')
        child1 = ChildEntity(id=1, name='child_1')
        child2 = ChildEntity(id=2, name='child_2')
        child3 = ChildEntity(id=3, name='child_3')
        parent1.add_to__children(child1, child2, child3)
        parent2 = ParentEntity(id=2, name='parent_2')
        child4 = ChildEntity(id=4, name='child_4')
        child5 = ChildEntity(id=5, name='child_5')
        child6 = ChildEntity(id=6, name='child_6')
        parent2.add_to__children(child4, child5, child6)
        root.add_to__children(parent1, parent2)
        
#        print(json.dumps(classUtil.to_dict(root), indent=2))
        
        second_child_expr = Field('children', 1)
        second_child = second_child_expr.evaluate(root)
        self.assertEqual(parent2, second_child)
        
        child_id_eq_2_expr = Field('children', Filter(Equals(Field('id'), Literal(2))))
        child_id_eq_2 = child_id_eq_2_expr.evaluate(root)
        self.assertEqual(parent2, child_id_eq_2)
        
        child_id_eq_2 = child_id_eq_2_expr.evaluate(parent1)
        self.assertEqual(child2, child_id_eq_2)
        
        child_name_eq_param_expr = Field('children', Filter(Equals(Field('name'), Parameter('name'))))
        child_name_eq_parent_1 = child_name_eq_param_expr.evaluate(root, name='parent_1')
        self.assertEqual(parent1, child_name_eq_parent_1)
        child_name_eq_parent_2 = child_name_eq_param_expr.evaluate(root, name='parent_2')
        self.assertEqual(parent2, child_name_eq_parent_2)
        
        child_id_ge_param_expr = Field('children', Filter(GreaterThan(Field('id'), Parameter('id'))))
        children_id_gt_4 = child_id_ge_param_expr.evaluate(parent2, id=4)
        self.assertEqual(2, len(children_id_gt_4))
        self.assertTrue(child4 not in children_id_gt_4)
        self.assertTrue(child5 in children_id_gt_4)
        self.assertTrue(child6 in children_id_gt_4)
                                       
        
    def test_expr_to_path(self):
        name_field = Field('name')
        self.assertEqual('name', name_field.to_path())
        
        items_field = Field('items', 1)
        self.assertEqual('items[1]', items_field.to_path())
        
        filtered_field = Field('items', Filter(Equals(Field('id'), Parameter('id'))))
        self.assertEqual('items[id==$id]', filtered_field.to_path())
        
        filtered_field = Field('items', Filter(And(Equals(Field('id'), Parameter('id')), GreaterThan(Field('total'), Literal(1.234)))))
        self.assertEqual('items[(id==$id&total>1.234)]', filtered_field.to_path())
        
    def test_path_to_expr(self):
        
        expr = ExpressionParser(Tokeniser(StringReader('name'))).get_expression()
        self.assertTrue(isinstance(expr, Field))
        self.assertEqual('name', expr.field)
        
    def test_path_with_index_to_expr(self):      
        expr = ExpressionParser(Tokeniser(StringReader('items[1]'))).get_expression()
        self.assertTrue(isinstance(expr, Field))
        self.assertEqual('items', expr.field)
        self.assertEqual(None, expr.list_filter)
        self.assertEqual(1, expr.list_index)
        
    def test_path_with_filter_to_expr(self):      
        expr = ExpressionParser(Tokeniser(StringReader('items[id==$id]'))).get_expression()
        self.assertTrue(isinstance(expr, Field))
        self.assertEqual('items', expr.field)
        self.assertEqual(None, expr.list_index)
        self.assertNotEqual(None, expr.list_filter)
        self.assertTrue(isinstance(expr.list_filter, Filter))
        self.assertTrue(isinstance(expr.list_filter.filter, Equals))
        self.assertTrue(isinstance(expr.list_filter.filter.lhs, Field))
        self.assertEquals('id', expr.list_filter.filter.lhs.field)
        self.assertTrue(isinstance(expr.list_filter.filter.rhs, Parameter))
        self.assertEquals('id', expr.list_filter.filter.rhs.parameter)
        
    def test_path_with_compound_filter_to_expr(self):      
        expr = ExpressionParser(Tokeniser(StringReader('items[(id==$id&total>1.234)]'))).get_expression()
        self.assertTrue(isinstance(expr, Field))
        self.assertEqual('items', expr.field)
        self.assertEqual(None, expr.list_index)
        self.assertNotEqual(None, expr.list_filter)
        self.assertTrue(isinstance(expr.list_filter, Filter))
        self.assertTrue(isinstance(expr.list_filter.filter, And))
        self.assertTrue(isinstance(expr.list_filter.filter.items[0].lhs, Field))
        self.assertEquals('id', expr.list_filter.filter.items[0].lhs.field)
        self.assertTrue(isinstance(expr.list_filter.filter.items[0].rhs, Parameter))
        self.assertEquals('id', expr.list_filter.filter.items[0].rhs.parameter)
        self.assertTrue(isinstance(expr.list_filter.filter.items[1], GreaterThan))
        self.assertTrue(isinstance(expr.list_filter.filter.items[1].lhs, Field))
        self.assertEquals('total', expr.list_filter.filter.items[1].lhs.field)
        self.assertTrue(isinstance(expr.list_filter.filter.items[1].rhs, Literal))
        self.assertEquals(1.234, expr.list_filter.filter.items[1].rhs.literal)
        self.assertEqual(2, len(expr.list_filter.filter.items))
        
class TestPath(unittest.TestCase):

    def test_evaluate_path(self):
        root = RootEntity(id=1, name='root_1')
        parent1 = ParentEntity(id=1, name='parent_1')
        child1 = ChildEntity(id=1, name='child_1')
        child2 = ChildEntity(id=2, name='child_2')
        child3 = ChildEntity(id=3, name='child_3')
        parent1.add_to__children(child1, child2, child3)
        parent2 = ParentEntity(id=2, name='parent_2')
        child4 = ChildEntity(id=4, name='child_4')
        child5 = ChildEntity(id=5, name='child_5')
        child6 = ChildEntity(id=6, name='child_6')
        parent2.add_to__children(child4, child5, child6)
        root.add_to__children(parent1, parent2)
        
        path = Path(Field('children'), 'name')
        names = path.evaluate(root)
        self.assertEqual(2, len(names))
        self.assertTrue('parent_1' in names)
        self.assertTrue('parent_2' in names)
        
        names = path.evaluate(parent1)
        self.assertEqual(3, len(names))
        self.assertTrue('child_1' in names)
        self.assertTrue('child_2' in names)
        self.assertTrue('child_3' in names)
                
    def test_evaluate_path_and_filter(self):
        root = RootEntity(id=1, name='root_1')
        parent1 = ParentEntity(id=1, name='parent_1')
        child1 = ChildEntity(id=1, name='child_1')
        child2 = ChildEntity(id=2, name='child_2')
        child3 = ChildEntity(id=3, name='child_3')
        parent1.add_to__children(child1, child2, child3)
        parent2 = ParentEntity(id=2, name='parent_2')
        child4 = ChildEntity(id=4, name='child_4')
        child5 = ChildEntity(id=5, name='child_5')
        child6 = ChildEntity(id=6, name='child_6')
        parent2.add_to__children(child4, child5, child6)
        root.add_to__children(parent1, parent2)
        
        path = Path(Path(Field('children'), 'children', Filter(GreaterThan(Field('id'), Literal(2)))), 'name')        
        names = path.evaluate(root)
        self.assertEqual(4, len(names))
        self.assertTrue('child_3' in names)
        self.assertTrue('child_4' in names)
        self.assertTrue('child_5' in names)
        self.assertTrue('child_6' in names)
        
    def test_expression_to_path(self):
        path = Path(Path(Field('children'), 'children', Filter(GreaterThan(Field('id'), Literal(2)))), 'name')
        self.assertEqual('children.children[id>2].name', path.to_path())      

    def test_path_to_expression(self):
        
        expr = ExpressionParser(Tokeniser(StringReader('children.children[id>2].name'))).get_expression()
        
        self.assertTrue(isinstance(expr, Path))
        self.assertEqual('name', expr.field)
        self.assertEqual(None, expr.list_index)
        self.assertEqual(None, expr.list_filter)
        self.assertTrue(isinstance(expr.path, Path))
        self.assertEqual('children', expr.path.field)
        self.assertEqual(None, expr.path.list_index)
        self.assertNotEqual(None, expr.path.list_filter)
        self.assertTrue(isinstance(expr.path.list_filter, Filter))
        self.assertTrue(isinstance(expr.path.list_filter.filter, GreaterThan))
        self.assertTrue(isinstance(expr.path.list_filter.filter.lhs, Field))
        self.assertEqual('id', expr.path.list_filter.filter.lhs.field)
        self.assertTrue(isinstance(expr.path.list_filter.filter.rhs, Literal))
        self.assertEqual(2, expr.path.list_filter.filter.rhs.literal)
        self.assertTrue(isinstance(expr.path.path, Field))
        self.assertEqual('children', expr.path.path.field)
        self.assertEqual(None, expr.path.path.list_index)
        self.assertEqual(None, expr.path.path.list_filter)

        
class TestLiteral(unittest.TestCase):
    
    def test_evaluate(self):
        literal = Literal(123)
        self.assertEqual(123, literal.evaluate({}))      
        
        literal = Literal(123.456)
        self.assertEqual(123.456, literal.evaluate({}))      
        
        literal = Literal('literal string')
        self.assertEqual('literal string', literal.evaluate({}))
        
        literal = Literal(True)
        self.assertEqual(True, literal.evaluate({}))
        
        literal = Literal(False)
        self.assertEqual(False, literal.evaluate({}))
        
    def test_expression_to_path(self):
        literal = Literal(123)
        self.assertEqual('123', literal.to_path())      
        
        literal = Literal(123.456)
        self.assertEqual('123.456', literal.to_path())      
        
        literal = Literal('literal string')
        self.assertEqual(TokenType.QUOTE.value+'literal string'+TokenType.QUOTE.value, literal.to_path())      
        
        literal = Literal(True)
        self.assertEqual('True', literal.to_path())      
        
        literal = Literal(False)
        self.assertEqual('False', literal.to_path())      
        
    def test_path_to_expression(self):
        expr = ExpressionParser(Tokeniser(StringReader('123'))).get_expression()
        self.assertTrue(isinstance(expr, Literal))
        self.assertEqual(123, expr.literal)      
        
        expr = ExpressionParser(Tokeniser(StringReader('123.456'))).get_expression()
        self.assertTrue(isinstance(expr, Literal))
        self.assertEqual(123.456, expr.literal)      
        
        expr = ExpressionParser(Tokeniser(StringReader('True'))).get_expression()
        self.assertTrue(isinstance(expr, Literal))
        self.assertEqual(True, expr.literal)      
        
        expr = ExpressionParser(Tokeniser(StringReader('False'))).get_expression()
        self.assertTrue(isinstance(expr, Literal))
        self.assertEqual(False, expr.literal)      
        
        expr = ExpressionParser(Tokeniser(StringReader(Q+'literal string'+Q))).get_expression()
        self.assertTrue(isinstance(expr, Literal))
        self.assertEqual('literal string', expr.literal)      
        
class TestParameter(unittest.TestCase):

    def test_evaluate(self):
        p = Parameter('parm')
        self.assertEqual(123, p.evaluate({}, parm=123))      
                
    def test_expression_to_path(self):
        p = Parameter('parm')
        self.assertEqual(TokenType.PARAMETER.value+'parm', p.to_path())      
        
    def test_path_to_expression(self):
        expr = ExpressionParser(Tokeniser(StringReader(TokenType.PARAMETER.value+'parm'))).get_expression()
        self.assertTrue(isinstance(expr, Parameter))
        self.assertEqual('parm', expr.parameter)      
        
class TestEquals(unittest.TestCase):

    def test_evaluate(self):
        p = Equals(Literal('abc'), Literal('abc'))
        self.assertEqual(True, p.evaluate({}))      
                
        p = Equals(Literal('ABC'), Literal('abc'))
        self.assertEqual(False, p.evaluate({}))      
                
    def test_expression_to_path(self):
        p = Equals(Literal('abc'), Literal('abc'))
        self.assertEqual(Q+'abc'+Q+'=='+Q+'abc'+Q, p.to_path())      

        p = Equals(Literal('ABC'), Literal('abc'))
        self.assertEqual(Q+'ABC'+Q+'=='+Q+'abc'+Q, p.to_path())
        
    def test_path_to_expression(self):
        expr = ExpressionParser(Tokeniser(StringReader(Q+'ABC'+Q+'=='+Q+'abc'+Q))).get_expression()
        self.assertTrue(isinstance(expr, Equals))
        self.assertTrue(isinstance(expr.lhs, Literal))
        self.assertEqual('ABC', expr.lhs.literal)      
        self.assertTrue(isinstance(expr.rhs, Literal))
        self.assertEqual('abc', expr.rhs.literal)      
        
    
class TestNotEquals(unittest.TestCase):

    def test_evaluate(self):
        p = NotEquals(Literal('abc'), Literal('abc'))
        self.assertEqual(False, p.evaluate({}))      
                
        p = NotEquals(Literal('ABC'), Literal('abc'))
        self.assertEqual(True, p.evaluate({}))      
                
    def test_expression_to_path(self):
        p = NotEquals(Literal('abc'), Literal('abc'))
        self.assertEqual(Q+'abc'+Q+'!='+Q+'abc'+Q, p.to_path())      

        p = NotEquals(Literal('ABC'), Literal('abc'))
        self.assertEqual(Q+'ABC'+Q+'!='+Q+'abc'+Q, p.to_path())
        
    def test_path_to_expression(self):
        expr = ExpressionParser(Tokeniser(StringReader(Q+'ABC'+Q+'!='+Q+'abc'+Q))).get_expression()
        self.assertTrue(isinstance(expr, NotEquals))
        self.assertTrue(isinstance(expr.lhs, Literal))
        self.assertEqual('ABC', expr.lhs.literal)      
        self.assertTrue(isinstance(expr.rhs, Literal))
        self.assertEqual('abc', expr.rhs.literal)      
        
    
class TestGreaterThan(unittest.TestCase):

    def test_evaluate(self):
        p = GreaterThan(Literal(101), Literal(100))
        self.assertEqual(True, p.evaluate({}))      
                
        p = GreaterThan(Literal(100), Literal(100))
        self.assertEqual(False, p.evaluate({}))      
                
    def test_expression_to_path(self):
        p = GreaterThan(Literal(101), Literal(100))
        self.assertEqual('101>100', p.to_path())      

        p = GreaterThan(Literal(100), Literal(100))
        self.assertEqual('100>100', p.to_path())
        
    def test_path_to_expression(self):
        expr = ExpressionParser(Tokeniser(StringReader('101>100'))).get_expression()
        self.assertTrue(isinstance(expr, GreaterThan))
        self.assertTrue(isinstance(expr.lhs, Literal))
        self.assertEqual(101, expr.lhs.literal)      
        self.assertTrue(isinstance(expr.rhs, Literal))
        self.assertEqual(100, expr.rhs.literal)      
        
    
class TestGreaterThanOrEqual(unittest.TestCase):

    def test_evaluate(self):
        p = GreaterThanOrEqual(Literal(100), Literal(100))
        self.assertEqual(True, p.evaluate({}))      
                
        p = GreaterThanOrEqual(Literal(99), Literal(100))
        self.assertEqual(False, p.evaluate({}))      
                
    def test_expression_to_path(self):
        p = GreaterThanOrEqual(Literal(100), Literal(100))
        self.assertEqual('100>=100', p.to_path())      

        p = GreaterThanOrEqual(Literal(99), Literal(100))
        self.assertEqual('99>=100', p.to_path())
        
    def test_path_to_expression(self):
        expr = ExpressionParser(Tokeniser(StringReader('100>=100'))).get_expression()
        self.assertTrue(isinstance(expr, GreaterThanOrEqual))
        self.assertTrue(isinstance(expr.lhs, Literal))
        self.assertEqual(100, expr.lhs.literal)      
        self.assertTrue(isinstance(expr.rhs, Literal))
        self.assertEqual(100, expr.rhs.literal)      
        
    
class TestLessThan(unittest.TestCase):

    def test_evaluate(self):
        p = LessThan(Literal(99), Literal(100))
        self.assertEqual(True, p.evaluate({}))      
                
        p = LessThan(Literal(100), Literal(100))
        self.assertEqual(False, p.evaluate({}))      
                
    def test_expression_to_path(self):
        p = LessThan(Literal(99), Literal(100))
        self.assertEqual('99<100', p.to_path())      

        p = LessThan(Literal(100), Literal(100))
        self.assertEqual('100<100', p.to_path())
        
    def test_path_to_expression(self):
        expr = ExpressionParser(Tokeniser(StringReader('99<100'))).get_expression()
        self.assertTrue(isinstance(expr, LessThan))
        self.assertTrue(isinstance(expr.lhs, Literal))
        self.assertEqual(99, expr.lhs.literal)      
        self.assertTrue(isinstance(expr.rhs, Literal))
        self.assertEqual(100, expr.rhs.literal)      
        
    
class TestLessThanOrEqual(unittest.TestCase):

    def test_evaluate(self):
        p = LessThanOrEqual(Literal(100), Literal(100))
        self.assertEqual(True, p.evaluate({}))      
                
        p = LessThanOrEqual(Literal(101), Literal(100))
        self.assertEqual(False, p.evaluate({}))      
                
    def test_expression_to_path(self):
        p = LessThanOrEqual(Literal(99), Literal(100))
        self.assertEqual('99<=100', p.to_path())      

        p = LessThanOrEqual(Literal(100), Literal(100))
        self.assertEqual('100<=100', p.to_path())
        
    def test_path_to_expression(self):
        expr = ExpressionParser(Tokeniser(StringReader('99<=100'))).get_expression()
        self.assertTrue(isinstance(expr, LessThanOrEqual))
        self.assertTrue(isinstance(expr.lhs, Literal))
        self.assertEqual(99, expr.lhs.literal)      
        self.assertTrue(isinstance(expr.rhs, Literal))
        self.assertEqual(100, expr.rhs.literal)      
        
        
class TestIsNull(unittest.TestCase):

    def test_evaluate(self):
        p = IsNull(Literal(100))
        self.assertEqual(False, p.evaluate({}))      
                
        p = IsNull(Literal(None))
        self.assertEqual(True, p.evaluate({}))      
                
    def test_expression_to_path(self):
        p = IsNull(Literal(100))
        self.assertEqual(' IsNull(100)', p.to_path())      
        
    def test_path_to_expression(self):
        expr = ExpressionParser(Tokeniser(StringReader('IsNull(100)'))).get_expression()
        self.assertTrue(isinstance(expr, IsNull))
        self.assertTrue(isinstance(expr.operand, Literal))
        self.assertEqual(100, expr.operand.literal)      
        
        
class TestIsNotNull(unittest.TestCase):

    def test_evaluate(self):
        p = IsNotNull(Literal(100))
        self.assertEqual(True, p.evaluate({}))      
                
        p = IsNotNull(Literal(None))
        self.assertEqual(False, p.evaluate({}))      
                
    def test_expression_to_path(self):
        p = IsNotNull(Literal(100))
        self.assertEqual(' IsNotNull(100)', p.to_path())      
        
    def test_path_to_expression(self):
        expr = ExpressionParser(Tokeniser(StringReader('IsNotNull(100)'))).get_expression()
        self.assertTrue(isinstance(expr, IsNotNull))
        self.assertTrue(isinstance(expr.operand, Literal))
        self.assertEqual(100, expr.operand.literal)      
        
    
class TestFilter(unittest.TestCase):

    def test_evaluate(self):
        
        root = RootEntity(id=1, name='root_1')
        parent1 = ParentEntity(id=1, name='parent_1')
        child1 = ChildEntity(id=1, name='child_1')
        child2 = ChildEntity(id=2, name='child_2')
        child3 = ChildEntity(id=3, name='child_3')
        parent1.add_to__children(child1, child2, child3)
        parent2 = ParentEntity(id=2, name='parent_2')
        child4 = ChildEntity(id=4, name='child_4')
        child5 = ChildEntity(id=5, name='child_5')
        child6 = ChildEntity(id=6, name='child_6')
        parent2.add_to__children(child4, child5, child6)
        root.add_to__children(parent1, parent2)

        f = Filter(Equals(Field('name'), Parameter('name')))
        self.assertEqual(root, f.evaluate(root, name='root_1'))      
        self.assertEqual(None, f.evaluate(root, name='root_2'))      
                                
    def test_expression_to_path(self):
        f = Filter(Equals(Field('name'), Parameter('name')))
        self.assertEqual('[name==$name]', f.to_path())      
        
    def test_path_to_expression(self):
        expr = ExpressionParser(Tokeniser(StringReader('[name==$name]'))).get_expression()
        self.assertTrue(isinstance(expr, Filter))
        self.assertTrue(isinstance(expr.filter, Equals))
        self.assertTrue(isinstance(expr.filter.lhs, Field))
        self.assertEqual('name', expr.filter.lhs.field)
        self.assertTrue(isinstance(expr.filter.rhs, Parameter))
        self.assertEqual('name', expr.filter.rhs.parameter)
        
    
class TestGroup(unittest.TestCase):

    def test_evaluate(self):
        g = Group(Literal(100), Literal(101))
        self.assertEqual((100, 101), g.evaluate({}))      
                
        g = Group(Literal(100))
        self.assertEqual((100,), g.evaluate({}))      
                
    def test_expression_to_path(self):
        g = Group(Literal(100), Literal(101))
        self.assertEqual('(100,101)', g.to_path())      
        
    def test_path_to_expression(self):
        expr = ExpressionParser(Tokeniser(StringReader('(100,101)'))).get_expression()
        self.assertTrue(isinstance(expr, Group))
        self.assertEqual(2, len(expr.items))
        self.assertTrue(isinstance(expr.items[0], Literal))
        self.assertEqual(100, expr.items[0].literal)   
        self.assertTrue(isinstance(expr.items[1], Literal))
        self.assertEqual(101, expr.items[1].literal)   
        
    
class TestAdd(unittest.TestCase):

    def test_evaluate(self):
        expr = Add(Literal(100), Literal(101))
        self.assertEqual(201, expr.evaluate({}))      
                
        expr = Add(Literal(100))
        self.assertEqual(100, expr.evaluate({}))      
                
    def test_expression_to_path(self):
        expr = Add(Literal(100), Literal(101))
        self.assertEqual('100+101', expr.to_path())      
        
    def test_path_to_expression(self):
        expr = ExpressionParser(Tokeniser(StringReader('100+101'))).get_expression()
        self.assertTrue(isinstance(expr, Add))
        self.assertEqual(2, len(expr.items))
        self.assertTrue(isinstance(expr.items[0], Literal))
        self.assertEqual(100, expr.items[0].literal)   
        self.assertTrue(isinstance(expr.items[1], Literal))
        self.assertEqual(101, expr.items[1].literal)   
        
    
class TestSubtract(unittest.TestCase):

    def test_evaluate(self):
        expr = Subtract(Literal(100), Literal(101))
        self.assertEqual(-1, expr.evaluate({}))      
                
        expr = Subtract(Literal(100))
        self.assertEqual(100, expr.evaluate({}))      
                
    def test_expression_to_path(self):
        expr = Subtract(Literal(100), Literal(101))
        self.assertEqual('100-101', expr.to_path())      
                
        expr = Subtract(Literal(100))
        self.assertEqual('100', expr.to_path())      
        
    def test_path_to_expression(self):
        expr = ExpressionParser(Tokeniser(StringReader('100-101'))).get_expression()
        self.assertTrue(isinstance(expr, Subtract))
        self.assertEqual(2, len(expr.items))
        self.assertTrue(isinstance(expr.items[0], Literal))
        self.assertEqual(100, expr.items[0].literal)   
        self.assertTrue(isinstance(expr.items[1], Literal))
        self.assertEqual(101, expr.items[1].literal)   
        
    
class TestMultiply(unittest.TestCase):

    def test_evaluate(self):
        expr = Multiply(Literal(100), Literal(101))
        self.assertEqual(10100, expr.evaluate({}))      
                
        expr = Multiply(Literal(100))
        self.assertEqual(100, expr.evaluate({}))      
                
    def test_expression_to_path(self):
        expr = Multiply(Literal(100), Literal(101))
        self.assertEqual('100*101', expr.to_path())      
                
        expr = Multiply(Literal(100))
        self.assertEqual('100', expr.to_path())      
        
    def test_path_to_expression(self):
        expr = ExpressionParser(Tokeniser(StringReader('100*101'))).get_expression()
        self.assertTrue(isinstance(expr, Multiply))
        self.assertEqual(2, len(expr.items))
        self.assertTrue(isinstance(expr.items[0], Literal))
        self.assertEqual(100, expr.items[0].literal)   
        self.assertTrue(isinstance(expr.items[1], Literal))
        self.assertEqual(101, expr.items[1].literal)   
        
    
class TestDivide(unittest.TestCase):

    def test_evaluate(self):
        expr = Divide(Literal(200), Literal(10))
        self.assertEqual(20, expr.evaluate({}))      
                
        expr = Divide(Literal(100))
        self.assertEqual(100, expr.evaluate({}))      
                
    def test_expression_to_path(self):
        expr = Divide(Literal(100), Literal(101))
        self.assertEqual('100/101', expr.to_path())      
                
        expr = Divide(Literal(100))
        self.assertEqual('100', expr.to_path())      
        
    def test_path_to_expression(self):
        expr = ExpressionParser(Tokeniser(StringReader('100/101'))).get_expression()
        self.assertTrue(isinstance(expr, Divide))
        self.assertEqual(2, len(expr.items))
        self.assertTrue(isinstance(expr.items[0], Literal))
        self.assertEqual(100, expr.items[0].literal)   
        self.assertTrue(isinstance(expr.items[1], Literal))
        self.assertEqual(101, expr.items[1].literal)   
        
    
class TestConcatenate(unittest.TestCase):

    def test_evaluate(self):
        expr = Concatenate(Literal('aaa'), Literal(123))
        self.assertEqual('aaa123', expr.evaluate({}))      
                
        expr = Concatenate(Literal('aaa'))
        self.assertEqual('aaa', expr.evaluate({}))      
                
    def test_expression_to_path(self):
        expr = Concatenate(Literal('aaa'), Literal(123))
        self.assertEqual(' Concat("aaa",123)', expr.to_path())      
                
        expr = Concatenate(Literal('aaa'))
        self.assertEqual(' Concat("aaa")', expr.to_path())      
        
    def test_path_to_expression(self):
        expr = ExpressionParser(Tokeniser(StringReader('Concat("aaa",123)'))).get_expression()
        self.assertTrue(isinstance(expr, Concatenate))
        self.assertEqual(2, len(expr.items))
        self.assertTrue(isinstance(expr.items[0], Literal))
        self.assertEqual('aaa', expr.items[0].literal)   
        self.assertTrue(isinstance(expr.items[1], Literal))
        self.assertEqual(123, expr.items[1].literal)   
        
    
class TestAnd(unittest.TestCase):

    def test_evaluate(self):
        expr = And(Literal(True), Literal(False))
        self.assertEqual(False, expr.evaluate({}))      
                
        expr = And(Literal(True), Literal(True))
        self.assertEqual(True, expr.evaluate({}))      
                
        expr = And(Literal(True))
        self.assertEqual(True, expr.evaluate({}))      
                
    def test_expression_to_path(self):
        expr = And(Literal(True), Literal(False))
        self.assertEqual('(True&False)', expr.to_path())      
                
        expr = And(Literal(True))
        self.assertEqual('(True)', expr.to_path())      
        
    def test_path_to_expression(self):
        expr = ExpressionParser(Tokeniser(StringReader('(True&False)'))).get_expression()
        self.assertTrue(isinstance(expr, And))
        self.assertEqual(2, len(expr.items))
        self.assertTrue(isinstance(expr.items[0], Literal))
        self.assertEqual(True, expr.items[0].literal)   
        self.assertTrue(isinstance(expr.items[1], Literal))
        self.assertEqual(False, expr.items[1].literal)   
      
        
class TestOr(unittest.TestCase):

    def test_evaluate(self):
        expr = Or(Literal(True), Literal(False))
        self.assertEqual(True, expr.evaluate({}))      
                
        expr = Or(Literal(False), Literal(False))
        self.assertEqual(False, expr.evaluate({}))      
                
        expr = Or(Literal(True))
        self.assertEqual(True, expr.evaluate({}))      
                
    def test_expression_to_path(self):
        expr = Or(Literal(True), Literal(False))
        self.assertEqual('(True|False)', expr.to_path())      
                
        expr = Or(Literal(True))
        self.assertEqual('(True)', expr.to_path())      
        
    def test_path_to_expression(self):
        expr = ExpressionParser(Tokeniser(StringReader('(True|False)'))).get_expression()
        self.assertTrue(isinstance(expr, Or))
        self.assertEqual(2, len(expr.items))
        self.assertTrue(isinstance(expr.items[0], Literal))
        self.assertEqual(True, expr.items[0].literal)   
        self.assertTrue(isinstance(expr.items[1], Literal))
        self.assertEqual(False, expr.items[1].literal)   
        
    
class TestNot(unittest.TestCase):

    def test_evaluate(self):
        expr = Not(Literal(True))
        self.assertEqual(False, expr.evaluate({}))      
                
        expr = Not(Literal(False))
        self.assertEqual(True, expr.evaluate({}))      
                
    def test_expression_to_path(self):
        expr = Not(Literal(True))
        self.assertEqual('!True', expr.to_path())      
        
    def test_path_to_expression(self):
        expr = ExpressionParser(Tokeniser(StringReader('!True'))).get_expression()
        self.assertTrue(isinstance(expr, Not))
        self.assertTrue(isinstance(expr.predicate, Literal))
        self.assertEqual(True, expr.predicate.literal)   
        
    
        

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()