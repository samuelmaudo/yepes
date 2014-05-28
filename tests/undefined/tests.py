# -*- coding:utf-8 -*-

from django import test

from yepes.types import Undefined


class UndefinedTest(test.SimpleTestCase):

    def test_undefined(self):
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

