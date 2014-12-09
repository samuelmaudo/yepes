# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from django import test
from django.core.exceptions import ValidationError

from yepes.validators import (
    PhoneNumberValidator,
    PostalCodeValidator,
)

class ValidatorsTest(test.SimpleTestCase):

    def test_phone_number(self):
        validate = PhoneNumberValidator()
        validate('+9-999-999-9999')
        validate('999-999-999-9999')
        validate('999 999 999 9999')
        validate('999-99999')
        validate('(999) / 999-99999')
        validate('+99-99-999-99999')
        validate('99-99-99-999-99999')
        validate('999')
        validate('9999-9999999')
        validate('99999-99999')
        validate('+99-99999-99999')
        validate('9-999999999')
        validate('(9999) 9999 9999')
        validate('99999999')
        validate('999999999999')
        validate('+99 999 9999 9999')
        validate('+99 (9999) 9999 9999')
        validate('999 9999 9999')
        validate('9999 9999')
        validate('+9999-999-999')
        validate('+999-999-9999')
        validate('+999-9999-9999')
        validate('+9999-999-9999')
        validate('9999-999-999')
        validate('+99 (9) 999 9999')
        validate('+99 (99) 999 9999')
        validate('+99 (999) 999 9999')
        validate('9 (999) 999 9999')
        validate('+99-9999-9999')
        validate('+99 9999 9999')
        validate('99 99 99 99')
        validate('99 99 99 99 99')
        validate('9 99 99 99 99')
        validate('+99 9 99 99 99 99')
        validate('99999 999999')
        validate('99999 999999-99')
        validate('+99 9999 999999')
        validate('(99999) 999999')
        validate('+99 (9999) 999999')
        validate('99999-999999')
        validate('99999/999999-99')
        validate('999 9999')
        validate('999-9999')
        validate('99-99999999')
        validate('999-9999999')
        validate('9999-9999')
        validate('+99 99 99999999')
        validate('+99 9 99999999')
        validate('999 99 999')
        validate('999-999-999')
        validate('99-999-99-99')
        validate('(99) 999-99-99')
        validate('9 9999 99-99-99')
        validate('9 (999) 999-99-99')
        validate('999 99 99 99')
        validate('999 999 999')
        validate('99 999 99 99')
        validate('999 999 99 99')
        validate('+99 99 999 99 99')
        validate('9999 999 999')
        validate('(999) 9999 9999')
        validate('(9999) 999 9999')
        validate('(99999) 99999')
        validate('(9999 99) 99999')
        validate('(9999 99) 9999')
        validate('9999 999 9999')
        validate('9999 999999')
        validate('9999 999 99 99')
        validate('(999) 999-9999')
        validate('9-999-999-9999')
        validate('999-999-9999')
        validate('9 999 999-9999')
        validate('(99) 9999 9999')
        validate('(99) 99 99 99 99')
        validate('99 9999 9999')
        validate('+99 9 9999 9999')
        validate('+99 999 999 999')
        validate('99 99 99')
        validate('999 999')
        validate('(999) 9999-9999')
        validate('+999 9999-9999')
        validate('99999999999')
        validate('(9999) 999-9999')
        validate('(99999) 99-9999')
        validate('(999) 999-999-9999')
        validate('99 9-999-9999')
        validate('(99) 9999-9999')
        validate('(99999) 9999-9999')
        validate('(999) 99-9999')
        validate('9-999 9999')
        with self.assertRaises(ValidationError):
            validate('9')
        with self.assertRaises(ValidationError):
            validate('99')
        with self.assertRaises(ValidationError):
            validate('9999999999999999')
        with self.assertRaises(ValidationError):
            validate('+999999999999999')
        with self.assertRaises(ValidationError):
            validate('9-9-9-9-9')
        with self.assertRaises(ValidationError):
            validate(' 99 99 ')
        with self.assertRaises(ValidationError):
            validate('a')
        with self.assertRaises(ValidationError):
            validate('++999999')
        with self.assertRaises(ValidationError):
            validate('99+99999')
        with self.assertRaises(ValidationError):
            validate('999()999')
        with self.assertRaises(ValidationError):
            validate('99(999)99(999)')
        with self.assertRaises(ValidationError):
            validate('999/999/999')
        with self.assertRaises(ValidationError):
            validate('999.999.9999')
        with self.assertRaises(ValidationError):
            validate('abc')
        with self.assertRaises(ValidationError):
            validate('ABC')
        with self.assertRaises(ValidationError):
            validate('--/--')
        with self.assertRaises(ValidationError):
            validate('&')

    def test_postal_code(self):
        validate = PostalCodeValidator()
        validate('999')
        validate('999 99')
        validate('999-9999')
        validate('999-999-9')
        validate('9999')
        validate('9999 A')
        validate('9999 AA')
        validate('9999 999')
        validate('9999 9999')
        validate('9999-999')
        validate('99999')
        validate('99999-999')
        validate('99999-9999')
        validate('99999-99999')
        validate('99999-999999')
        validate('9999999')
        validate('A9 9AA')
        validate('A9A 9AA')
        validate('A99 9AA')
        validate('AA9 9AA')
        validate('AA9A 9AA')
        validate('AA99 9AA')
        validate('AA999')
        validate('AA9999')
        validate('AAAA 9AA')
        validate('AA-9999')
        validate('A999')
        validate('A9999AAA')
        validate('AAAA9AA')
        validate('AAA9999')
        validate('AAA 9999')
        with self.assertRaises(ValidationError):
            validate('9')
        with self.assertRaises(ValidationError):
            validate('99')
        with self.assertRaises(ValidationError):
            validate('A')
        with self.assertRaises(ValidationError):
            validate('AA')
        with self.assertRaises(ValidationError):
            validate('999999999999999')
        with self.assertRaises(ValidationError):
            validate('AAAAAAAAAAAAAAA')
        with self.assertRaises(ValidationError):
            validate('9-9-9-9-9')
        with self.assertRaises(ValidationError):
            validate(' 99 99 ')
        with self.assertRaises(ValidationError):
            validate('+999')
        with self.assertRaises(ValidationError):
            validate('(99)999')
        with self.assertRaises(ValidationError):
            validate('99/999')
        with self.assertRaises(ValidationError):
            validate('99.999')
        with self.assertRaises(ValidationError):
            validate('-- --')
        with self.assertRaises(ValidationError):
            validate('&')

