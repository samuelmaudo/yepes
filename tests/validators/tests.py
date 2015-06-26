# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from django import test
from django.core.exceptions import ValidationError

from yepes.validators import (
    CharSetValidator,
    ColorValidator,
    FormulaValidator,
    IdentifierValidator,
    PhoneNumberValidator,
    PostalCodeValidator,
    RestrictedEmailValidator,
)

class ValidatorsTest(test.SimpleTestCase):

    def test_charset(self):
        validator = CharSetValidator('abcdef')
        def assertValid(value):
            self.assertTrue(validator.validate(value))
            validator(value)

        def assertNotValid(value):
            self.assertFalse(validator.validate(value))
            with self.assertRaises(ValidationError):
                validator(value)

        assertValid('abcdef')
        assertValid('dadadada')
        assertNotValid('aBcDeF')
        assertNotValid('DADADADA')
        assertNotValid('uy')
        assertNotValid('a-f')

        validator = CharSetValidator('abcdefABCDEF')
        def assertValid(value):
            self.assertTrue(validator.validate(value))
            validator(value)

        def assertNotValid(value):
            self.assertFalse(validator.validate(value))
            with self.assertRaises(ValidationError):
                validator(value)

        assertValid('abcdef')
        assertValid('dadadada')
        assertValid('aBcDeF')
        assertValid('DADADADA')
        assertNotValid('uy')
        assertNotValid('a-f')

    def test_charset_with_range(self):
        validator = CharSetValidator('a-f')
        def assertValid(value):
            self.assertTrue(validator.validate(value))
            validator(value)

        def assertNotValid(value):
            self.assertFalse(validator.validate(value))
            with self.assertRaises(ValidationError):
                validator(value)

        assertValid('abcdef')
        assertValid('dadadada')
        assertNotValid('aBcDeF')
        assertNotValid('DADADADA')
        assertNotValid('uy')
        assertNotValid('a-f')

        validator = CharSetValidator('a-fA-F')
        def assertValid(value):
            self.assertTrue(validator.validate(value))
            validator(value)

        def assertNotValid(value):
            self.assertFalse(validator.validate(value))
            with self.assertRaises(ValidationError):
                validator(value)

        assertValid('abcdef')
        assertValid('dadadada')
        assertValid('aBcDeF')
        assertValid('DADADADA')
        assertNotValid('uy')
        assertNotValid('a-f')

    def test_color(self):
        validator = ColorValidator()
        def assertValid(value):
            self.assertTrue(validator.validate(value))
            validator(value)

        def assertNotValid(value):
            self.assertFalse(validator.validate(value))
            with self.assertRaises(ValidationError):
                validator(value)

        assertValid('#5DC1B9')
        assertValid('#5dc1b9')
        assertValid('#fff')
        assertValid('#fffFFF')
        assertNotValid('5DC1B9')
        assertNotValid('5dc1b9')
        assertNotValid('fff')
        assertNotValid('fffFFF')
        assertNotValid('#12')
        assertNotValid('#1234')
        assertNotValid('#12345678')
        assertNotValid('#hijKLM')

    def test_formula(self):
        validator = FormulaValidator()
        def assertValid(value):
            self.assertTrue(validator.validate(value))
            validator(value)

        def assertNotValid(value):
            self.assertFalse(validator.validate(value))
            with self.assertRaises(ValidationError):
                validator(value)

        assertValid('1 * 3 ** 5')
        assertValid('a * b ** c')
        assertValid('x * y ** z')
        assertNotValid('*')
        assertNotValid('not')
        assertNotValid('* 1')
        assertNotValid('1 *')
        assertNotValid('1 |/ 1')
        assertNotValid('1 * (10 - 3')
        assertNotValid('a * b)')

    def test_formula_with_variables(self):
        validator = FormulaValidator(['a', 'b', 'c'])
        def assertValid(value):
            self.assertTrue(validator.validate(value))
            validator(value)

        def assertNotValid(value):
            self.assertFalse(validator.validate(value))
            with self.assertRaises(ValidationError):
                validator(value)

        assertValid('1 * 3 ** 5')
        assertValid('a * b ** c')
        assertNotValid('x * y ** z')
        assertNotValid('*')
        assertNotValid('not')
        assertNotValid('* 1')
        assertNotValid('1 *')
        assertNotValid('1 |/ 1')
        assertNotValid('1 * (10 - 3')
        assertNotValid('a * b)')

    def test_identifier(self):
        validator = IdentifierValidator()
        def assertValid(value):
            self.assertTrue(validator.validate(value))
            validator(value)

        def assertNotValid(value):
            self.assertFalse(validator.validate(value))
            with self.assertRaises(ValidationError):
                validator(value)

        assertValid('variable')
        assertValid('variable_123')
        assertValid('_')
        assertValid('_variable')
        assertValid('variable_')
        assertValid('__variable__')
        assertValid('UpperCamelCase')
        assertValid('lowerCamelCase')
        assertValid('UPPER_CASE_WITH_UNDERSCORES')
        assertValid('lower_case_with_underscores')
        assertValid('Mixed_Case_With_Underscores')
        assertNotValid('123_variable')
        assertNotValid('z%.# +ç@')
        assertNotValid('UPPER-CASE-WITH-DASHES')
        assertNotValid('lower-case-with-dashes')
        assertNotValid('Mixed-Case-With-Dashes')

    def test_phone_number(self):
        validator = PhoneNumberValidator()
        def assertValid(value):
            self.assertTrue(validator.validate(value))
            validator(value)

        def assertNotValid(value):
            self.assertFalse(validator.validate(value))
            with self.assertRaises(ValidationError):
                validator(value)

        assertValid('+9-999-999-9999')
        assertValid('999-999-999-9999')
        assertValid('999 999 999 9999')
        assertValid('999-99999')
        assertValid('(999) / 999-99999')
        assertValid('+99-99-999-99999')
        assertValid('99-99-99-999-99999')
        assertValid('999')
        assertValid('9999-9999999')
        assertValid('99999-99999')
        assertValid('+99-99999-99999')
        assertValid('9-999999999')
        assertValid('(9999) 9999 9999')
        assertValid('99999999')
        assertValid('999999999999')
        assertValid('+99 999 9999 9999')
        assertValid('+99 (9999) 9999 9999')
        assertValid('999 9999 9999')
        assertValid('9999 9999')
        assertValid('+9999-999-999')
        assertValid('+999-999-9999')
        assertValid('+999-9999-9999')
        assertValid('+9999-999-9999')
        assertValid('9999-999-999')
        assertValid('+99 (9) 999 9999')
        assertValid('+99 (99) 999 9999')
        assertValid('+99 (999) 999 9999')
        assertValid('9 (999) 999 9999')
        assertValid('+99-9999-9999')
        assertValid('+99 9999 9999')
        assertValid('99 99 99 99')
        assertValid('99 99 99 99 99')
        assertValid('9 99 99 99 99')
        assertValid('+99 9 99 99 99 99')
        assertValid('99999 999999')
        assertValid('99999 999999-99')
        assertValid('+99 9999 999999')
        assertValid('(99999) 999999')
        assertValid('+99 (9999) 999999')
        assertValid('99999-999999')
        assertValid('99999/999999-99')
        assertValid('999 9999')
        assertValid('999-9999')
        assertValid('99-99999999')
        assertValid('999-9999999')
        assertValid('9999-9999')
        assertValid('+99 99 99999999')
        assertValid('+99 9 99999999')
        assertValid('999 99 999')
        assertValid('999-999-999')
        assertValid('99-999-99-99')
        assertValid('(99) 999-99-99')
        assertValid('9 9999 99-99-99')
        assertValid('9 (999) 999-99-99')
        assertValid('999 99 99 99')
        assertValid('999 999 999')
        assertValid('99 999 99 99')
        assertValid('999 999 99 99')
        assertValid('+99 99 999 99 99')
        assertValid('9999 999 999')
        assertValid('(999) 9999 9999')
        assertValid('(9999) 999 9999')
        assertValid('(99999) 99999')
        assertValid('(9999 99) 99999')
        assertValid('(9999 99) 9999')
        assertValid('9999 999 9999')
        assertValid('9999 999999')
        assertValid('9999 999 99 99')
        assertValid('(999) 999-9999')
        assertValid('9-999-999-9999')
        assertValid('999-999-9999')
        assertValid('9 999 999-9999')
        assertValid('(99) 9999 9999')
        assertValid('(99) 99 99 99 99')
        assertValid('99 9999 9999')
        assertValid('+99 9 9999 9999')
        assertValid('+99 999 999 999')
        assertValid('99 99 99')
        assertValid('999 999')
        assertValid('(999) 9999-9999')
        assertValid('+999 9999-9999')
        assertValid('99999999999')
        assertValid('(9999) 999-9999')
        assertValid('(99999) 99-9999')
        assertValid('(999) 999-999-9999')
        assertValid('99 9-999-9999')
        assertValid('(99) 9999-9999')
        assertValid('(99999) 9999-9999')
        assertValid('(999) 99-9999')
        assertValid('9-999 9999')
        assertNotValid('9')
        assertNotValid('9')
        assertNotValid('99')
        assertNotValid('9999999999999999')
        assertNotValid('+999999999999999')
        assertNotValid('9-9-9-9-9')
        assertNotValid(' 99 99 ')
        assertNotValid('a')
        assertNotValid('++999999')
        assertNotValid('99+99999')
        assertNotValid('999()999')
        assertNotValid('99(999)99(999)')
        assertNotValid('999/999/999')
        assertNotValid('999.999.9999')
        assertNotValid('abc')
        assertNotValid('ABC')
        assertNotValid('--/--')
        assertNotValid('&')

    def test_postal_code(self):
        validator = PostalCodeValidator()
        def assertValid(value):
            self.assertTrue(validator.validate(value))
            validator(value)

        def assertNotValid(value):
            self.assertFalse(validator.validate(value))
            with self.assertRaises(ValidationError):
                validator(value)

        assertValid('999')
        assertValid('999 99')
        assertValid('999-9999')
        assertValid('999-999-9')
        assertValid('9999')
        assertValid('9999 A')
        assertValid('9999 AA')
        assertValid('9999 999')
        assertValid('9999 9999')
        assertValid('9999-999')
        assertValid('99999')
        assertValid('99999-999')
        assertValid('99999-9999')
        assertValid('99999-99999')
        assertValid('99999-999999')
        assertValid('9999999')
        assertValid('A9 9AA')
        assertValid('A9A 9AA')
        assertValid('A99 9AA')
        assertValid('AA9 9AA')
        assertValid('AA9A 9AA')
        assertValid('AA99 9AA')
        assertValid('AA999')
        assertValid('AA9999')
        assertValid('AAAA 9AA')
        assertValid('AA-9999')
        assertValid('A999')
        assertValid('A9999AAA')
        assertValid('AAAA9AA')
        assertValid('AAA9999')
        assertValid('AAA 9999')
        assertNotValid('9')
        assertNotValid('99')
        assertNotValid('A')
        assertNotValid('AA')
        assertNotValid('999999999999999')
        assertNotValid('AAAAAAAAAAAAAAA')
        assertNotValid('9-9-9-9-9')
        assertNotValid(' 99 99 ')
        assertNotValid('+999')
        assertNotValid('(99)999')
        assertNotValid('99/999')
        assertNotValid('99.999')
        assertNotValid('-- --')
        assertNotValid('&')

    def test_restricted_email(self):
        validator = RestrictedEmailValidator()
        def assertValid(value):
            self.assertTrue(validator.validate(value))
            validator(value)

        def assertNotValid(value):
            self.assertFalse(validator.validate(value))
            with self.assertRaises(ValidationError):
                validator(value)

        # Valid and common.
        assertValid('niceandsimple@example.com')
        assertValid('very.common@example.com')
        assertValid('a.little.lengthy.but.fine@dept.example.com')
        assertValid('disposable.style.email.with+symbol@example.com')
        assertValid('other.email-with-dash@example.com')
        # Valid according to standard but uncommon.
        assertNotValid(r'"much.more unusual"@example.com')
        assertNotValid(r'"very.unusual.@.unusual.com"@example.com')
        assertNotValid(r'"very.(),:;<>[]\".VERY.\"very@\\ \"very\".unusual"@strange.example.com')
        assertNotValid(r'admin@mailserver1')
        assertNotValid(r"#!$%&'*+-/=?^_`{}|~@example.org")
        assertNotValid(r'"()<>[]:,;@\\\"!#$%&\'*+-/=?^_`{}| ~.a"@example.org')
        assertNotValid(r'" "@example.org')
        assertNotValid(r'üñîçøðé@example.com')
        assertNotValid(r'jsmith@üñîçøðé.com')
        assertNotValid(r'jsmith@[192.168.2.1')
        assertNotValid(r'jsmith@[IPv6:2001:db8::1]')
        # Not valid.
        assertNotValid(r'Abc.example.com')
        assertNotValid(r'A@b@c@example.com')
        assertNotValid(r'a"b(c)d,e:f;g<h>i[j\k]l@example.com')
        assertNotValid(r'just"not"right@example.com')
        assertNotValid(r'this is"not\allowed@example.com')
        assertNotValid(r'this\ still\"not\\allowed@example.com')
        assertNotValid(r'john..doe@example.com')
        assertNotValid(r'john.doe@example..com')

