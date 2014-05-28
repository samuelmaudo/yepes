# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from decimal import Decimal

from django import test
from django.core.exceptions import ValidationError

from yepes.tests.formula.models import TestModel as Model
from yepes.types import Formula


class FormulaTest(test.SimpleTestCase):

    def test_logical(self):
        f = Formula('True and False')
        self.assertEqual(
                f.calculate(),
                False)
        f = Formula('true OR fAlSe')
        self.assertEqual(
                f.calculate(),
                True)
        f = Formula('NOt truE')
        self.assertEqual(
                f.calculate(),
                False)
        f = Formula('not 3')
        self.assertEqual(
                f.calculate(),
                False)
        f = Formula('2 and 3')
        self.assertEqual(
                f.calculate(),
                Decimal('3'))
        f = Formula('2 or 3')
        self.assertEqual(
                f.calculate(),
                Decimal('2'))

    def test_comparison(self):
        f = Formula('3 < 4')
        self.assertEqual(
                f.calculate(),
                True)
        f = Formula('3 <= 4')
        self.assertEqual(
                f.calculate(),
                True)
        f = Formula('3 == 4')
        self.assertEqual(
                f.calculate(),
                False)
        f = Formula('3 != 4')
        self.assertEqual(
                f.calculate(),
                True)
        f = Formula('3 <> 4')
        self.assertEqual(
                f.calculate(),
                True)
        f = Formula('3 > 4')
        self.assertEqual(
                f.calculate(),
                False)
        f = Formula('3 >= 4')
        self.assertEqual(
                f.calculate(),
                False)

    def test_mathematical(self):
        f = Formula('2+2')
        self.assertEqual(
                f.calculate(),
                Decimal('4'))
        f = Formula('2 + 2')
        self.assertEqual(
                f.calculate(),
                Decimal('4'))
        f = Formula('-2')
        self.assertEqual(
                f.calculate(),
                Decimal('-2'))
        f = Formula('- 2')
        self.assertEqual(
                f.calculate(),
                Decimal('-2'))
        f = Formula('2. + .2 - 1.1')
        self.assertEqual(
                f.calculate(),
                Decimal('1.1'))
        f = Formula('3 + 3')
        self.assertEqual(
                f.calculate(),
                Decimal('6'))
        f = Formula('3 - 3')
        self.assertEqual(
                f.calculate(),
                Decimal('0'))
        f = Formula('3 * 3')
        self.assertEqual(
                f.calculate(),
                Decimal('9'))
        f = Formula('3 ** 3')
        self.assertEqual(
                f.calculate(),
                Decimal('27'))
        f = Formula('3 / 3')
        self.assertEqual(
                f.calculate(),
                Decimal('1'))
        f = Formula('3 // 3')
        self.assertEqual(
                f.calculate(),
                Decimal('1'))
        f = Formula('3 % 3')
        self.assertEqual(
                f.calculate(),
                Decimal('0'))

    def test_variables(self):
        f = Formula('largo * ancho * alto / 4000')
        f.largo = 30
        f.ancho = 20
        f.alto = 10
        self.assertEqual(
                f.calculate(),
                Decimal('1.5'))
        f = Formula('(largo * ancho * alto) / 4000')
        self.assertEqual(
                f.calculate(largo=30, ancho=20, alto=10),
                Decimal('1.5'))
        f = Formula('(peso <= 10) and ((volumen / 4000) <= 10)')
        self.assertEqual(
                f.calculate(peso=3.8, volumen=1.5),
                True)

    def test_syntax_errors(self):
        with self.assertRaisesRegexp(SyntaxError, 'invalid syntax'):
            Formula('*').calculate()
        with self.assertRaisesRegexp(SyntaxError, 'invalid syntax'):
            Formula('not').calculate()
        with self.assertRaisesRegexp(SyntaxError, 'invalid syntax'):
            Formula('* 1').calculate()
        with self.assertRaisesRegexp(SyntaxError, 'invalid syntax'):
            Formula('1 *').calculate()
        #with self.assertRaisesRegexp(SyntaxError, 'invalid syntax'):
            #Formula('1 1').calculate()
        #with self.assertRaisesRegexp(SyntaxError, 'invalid syntax'):
            #Formula('1 not 1').calculate()
        with self.assertRaisesRegexp(SyntaxError, 'unknown variable: "x"'):
            Formula('1 x 1').calculate()
        with self.assertRaisesRegexp(SyntaxError, 'unknown operator: "|/"'):
            Formula('1 |/ 1').calculate()
        #with self.assertRaisesRegexp(SyntaxError, 'unknown variable: "var"'):
            #Formula('var * var').calculate()
        with self.assertRaisesRegexp(SyntaxError, 'improperly closed parentheses'):
            Formula('1 * (10 - 3').calculate()
        with self.assertRaisesRegexp(SyntaxError, 'improperly closed parentheses'):
            Formula('var * var)').calculate(var=1)
        with self.assertRaisesRegexp(SyntaxError, 'improperly closed parentheses'):
            Formula('var * var)').calculate(var=1)


class FormulaFieldTest(test.TestCase):

    def test_basic(self):
        instance = Model()
        instance.permissive_formula = '1 * 3 ** 5'
        self.assertIsInstance(instance.permissive_formula, Formula)
        self.assertEqual(instance.permissive_formula.calculate(), 243)
        instance.full_clean()
        self.assertIsInstance(instance.permissive_formula, Formula)
        self.assertEqual(instance.permissive_formula.calculate(), 243)

        instance.permissive_formula = 'x * y ** z'
        instance.full_clean()
        instance.permissive_formula = 'a * b ** c'
        instance.full_clean()

        instance.restricted_formula = '1 * 3 ** 5'
        self.assertIsInstance(instance.restricted_formula, Formula)
        self.assertEqual(instance.restricted_formula.calculate(), 243)
        instance.full_clean()
        self.assertIsInstance(instance.restricted_formula, Formula)
        self.assertEqual(instance.restricted_formula.calculate(), 243)

        instance.restricted_formula = 'x * y ** z'
        instance.full_clean()
        instance.restricted_formula = 'a * b ** c'
        with self.assertRaises(ValidationError):
            instance.full_clean()

