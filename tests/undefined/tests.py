# -*- coding:utf-8 -*-

try:
    import cPickle as pickle
except ImportError:
    import pickle

from django import test

from yepes.types import Undefined, UndefinedType


class UndefinedTest(test.SimpleTestCase):

    def test_value(self):
        self.assertEqual(Undefined, Undefined)
        self.assertNotEqual(Undefined, True)
        self.assertNotEqual(Undefined, False)
        self.assertNotEqual(Undefined, None)
        self.assertIs(Undefined, Undefined)
        self.assertIsNot(Undefined, True)
        self.assertIsNot(Undefined, False)
        self.assertIsNot(Undefined, None)
        self.assertFalse(Undefined)
        self.assertEqual(str(Undefined), 'Undefined')
        self.assertEqual(repr(Undefined), 'Undefined')
        id(Undefined)
        hash(Undefined)
        type(Undefined)

    def test_singleton(self):
        undefined_1 = UndefinedType()
        undefined_2 = UndefinedType()
        self.assertIs(undefined_1, Undefined)
        self.assertIs(undefined_2, Undefined)

        undefined_3 = UndefinedType.__new__(UndefinedType) # Used in pickle load method
        undefined_4 = UndefinedType.__new__(UndefinedType)
        self.assertIs(undefined_3, Undefined)
        self.assertIs(undefined_4, Undefined)

        undefined_5 = pickle.loads(pickle.dumps(Undefined, protocol=0))
        undefined_6 = pickle.loads(pickle.dumps(Undefined, protocol=1))
        undefined_7 = pickle.loads(pickle.dumps(Undefined, protocol=2))
        undefined_8 = pickle.loads(pickle.dumps(Undefined, protocol= pickle.HIGHEST_PROTOCOL))
        undefined_9 = pickle.loads(pickle.dumps(Undefined))
        #self.assertIs(undefined_5, Undefined)
        #self.assertIs(undefined_6, Undefined)
        self.assertIs(undefined_7, Undefined)
        self.assertIs(undefined_8, Undefined)
        #self.assertIs(undefined_9, Undefined)

