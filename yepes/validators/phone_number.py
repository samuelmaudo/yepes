# -*- coding:utf-8 -*-

from __future__ import unicode_literals

import re

from django.utils.encoding import force_text
from django.utils.translation import ugettext_lazy as _

from yepes.validators.base import Validator


class PhoneNumberValidator(Validator):
    """
    Checks if the value is a valid phone number.
    """
    message = _('Enter a valid phone number.')

    def validate(self, value):
        value = force_text(value)
        digits = len(re.findall(r'[0-9]', value))
        plus_sign = len(re.findall(r'^\+', value))
        hyphens = len(re.findall(r'\-', value))
        spaces = len(re.findall(r' ', value))
        open_parentheses = len(re.findall(r'\((?!\))', value))
        close_parentheses = len(re.findall(r'\)', value))
        slashes = len(re.findall(r'/', value))
        return (
            len(value) == (digits + plus_sign + hyphens + spaces
                           + open_parentheses + close_parentheses
                           + slashes)
            and digits >= 3
            and digits <= (15 if not plus_sign else 14)
            and hyphens + spaces <= (digits / 2)
            and open_parentheses == close_parentheses
            and open_parentheses <= 1
            and close_parentheses <= 1
            and slashes <= 1
        )

