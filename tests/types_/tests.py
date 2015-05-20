# -*- coding:utf-8 -*-

from decimal import Decimal
try:
    import cPickle as pickle
except ImportError:
    import pickle

from django import test

from yepes.types import Bit, Formula, Undefined, UndefinedType


class BitTest(test.SimpleTestCase):

    def test_int(self):
        bit = Bit(0)
        self.assertEqual(int(bit), 0)
        self.assertEqual(bool(bit), False)
        self.assertTrue(not bit)
        self.assertEqual(str(bit), '0')
        self.assertEqual(repr(bit), '<Bit: 0>')
        bit = Bit(0b1100)
        self.assertEqual(int(bit), 0b1100)
        self.assertEqual(bool(bit), True)
        self.assertFalse(not bit)
        self.assertEqual(str(bit), '1100')
        self.assertEqual(repr(bit), '<Bit: 1100>')

    def test_comparison(self):
        self.assertEqual(Bit(0), Bit(0))
        self.assertNotEqual(Bit(1), Bit(0))
        self.assertEqual(Bit(0), 0)
        self.assertNotEqual(Bit(1), 0)

    def test_and(self):
        self.assertEqual(1 & Bit(0), 0)
        self.assertEqual(1 & Bit(1), 1)
        self.assertEqual(0b0110 & Bit(0b1100), 0b0100)
        self.assertEqual(Bit(1) & Bit(0), 0)
        self.assertEqual(Bit(1) & Bit(1), 1)
        self.assertEqual(Bit(0b0110) & Bit(0b1100), 0b0100)

    def test_or(self):
        self.assertEqual(1 | Bit(0), 1)
        self.assertEqual(1 | Bit(1), 1)
        self.assertEqual(0b0110 | Bit(0b1100), 0b1110)
        self.assertEqual(Bit(1) | Bit(0), 1)
        self.assertEqual(Bit(1) | Bit(1), 1)
        self.assertEqual(Bit(0b0110) | Bit(0b1100), 0b1110)

    def test_xor(self):
        self.assertEqual(1 ^ Bit(0), 1)
        self.assertEqual(1 ^ Bit(1), 0)
        self.assertEqual(0b0110 ^ Bit(0b1100), 0b1010)
        self.assertEqual(Bit(1) ^ Bit(0), 1)
        self.assertEqual(Bit(1) ^ Bit(1), 0)
        self.assertEqual(Bit(0b0110) ^ Bit(0b1100), 0b1010)

    def test_invert(self):
        self.assertEqual(~Bit(1), 0)
        self.assertEqual(~Bit(0), 1)
        self.assertEqual(~Bit(0b100110), 0b011001)


class FormulaTest(test.SimpleTestCase):

    def checkFormula(self, formula, result):
        self.assertEqual(Formula(formula).calculate(), result)

    def test_logical(self):
        self.checkFormula('True and False', False)
        self.checkFormula('true OR fAlSe', True)
        self.checkFormula('NOt truE', False)
        self.checkFormula('not 3', False)
        self.checkFormula('2 and 3', Decimal('3'))
        self.checkFormula('2 or 3', Decimal('2'))

    def test_comparison(self):
        self.checkFormula('3 < 4', True)
        self.checkFormula('3 <= 4', True)
        self.checkFormula('3 == 4', False)
        self.checkFormula('3 != 4', True)
        self.checkFormula('3 <> 4', True)
        self.checkFormula('3 > 4', False)
        self.checkFormula('3 >= 4', False)

    def test_mathematical(self):
        self.checkFormula('2+2', Decimal('4'))
        self.checkFormula('2 + 2', Decimal('4'))
        self.checkFormula('-2', Decimal('-2'))
        self.checkFormula('- 2', Decimal('-2'))
        self.checkFormula('2. + .2 - 1.1', Decimal('1.1'))
        self.checkFormula('3 + 3', Decimal('6'))
        self.checkFormula('3 - 3', Decimal('0'))
        self.checkFormula('3 * 3', Decimal('9'))
        self.checkFormula('3 ** 3', Decimal('27'))
        self.checkFormula('3 / 3', Decimal('1'))
        self.checkFormula('3 // 3', Decimal('1'))
        self.checkFormula('3 % 3', Decimal('0'))

    def test_variables(self):
        f = Formula('largo * ancho * alto / 4000')
        f.largo = 30
        f.ancho = 20
        f.alto = 10
        self.assertEqual(
            f.calculate(),
            Decimal('1.5'),
        )
        f = Formula('(largo * ancho * alto) / 4000')
        self.assertEqual(
            f.calculate(largo=30, ancho=20, alto=10),
            Decimal('1.5'),
        )
        f = Formula('(peso <= 10) and ((volumen / 4000) <= 10)')
        self.assertEqual(
            f.calculate(peso=3.8, volumen=1.5),
            True,
        )

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

