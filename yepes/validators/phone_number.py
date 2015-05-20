# -*- coding:utf-8 -*-

from __future__ import unicode_literals

import re

from django.utils.encoding import smart_str
from django.utils.translation import ugettext_lazy as _

from yepes.validators import BaseValidator


class PhoneNumberValidator(BaseValidator):
    """
    Checks if the value is a valid phone number.
    """

    code = 'invalid_phone_number'
    message = _('Enter a valid phone number.')

    def __call__(self, value):
        value = smart_str(value)
        digits = len(re.findall(r'[0-9]', value))
        plus_sign = len(re.findall(r'^\+', value))
        hyphens = len(re.findall(r'\-', value))
        spaces = len(re.findall(r' ', value))
        open_parentheses = len(re.findall(r'\((?=.+\))', value))
        close_parentheses = len(re.findall(r'\)', value))
        slashes = len(re.findall(r'/', value))
        valid_chars = (digits
                        + plus_sign
                        + hyphens + spaces
                        + open_parentheses + close_parentheses
                        + slashes)
        if (len(value) != valid_chars
                or digits < 3
                or digits > (15 if not plus_sign else 14)
                or hyphens + spaces > (digits / 2)
                or open_parentheses != close_parentheses
                or open_parentheses > 1
                or close_parentheses > 1
                or slashes > 1):
            self.invalid(value)

