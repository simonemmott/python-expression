'''
Created on 28 Dec 2018

@author: simon
'''
import unittest
from test_entities import *
from expressions import *


class TestExpressions(unittest.TestCase):

    def test_field(self):
        eA_1 = EntityA(id=1, name='EA_1', description='This is EA 1')
        eA_2 = EntityA(id=2, name='EA_2', description='This is EA 2')
        eC_1 = EntityA(id=1, name='EC_1', description='This is EC 1')
        eC_2 = EntityA(id=2, name='EC_2', description='This is EC 2')
        
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
        
        


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()