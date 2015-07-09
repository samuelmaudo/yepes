# -*- coding:utf-8 -*-

from __future__ import unicode_literals

import re

from django.utils.encoding import force_text
from django.utils.translation import ugettext_lazy as _

from yepes.validators.base import Validator

CLOSE_PARENTHESES = re.compile(r'\)')
DIGITS_RE = re.compile(r'[0-9]')
HYPHENS_RE = re.compile(r'-')
OPEN_PARENTHESES = re.compile(r'\((?!\))')
PLUS_SIGN_RE = re.compile(r'\A\+')
SLASHES = re.compile(r'/')
SPACES_RE = re.compile(r' ')


class PhoneNumberValidator(Validator):
    """
    Checks if the value is a valid phone number.
    """
    message = _('Enter a valid phone number.')

    def validate(self, value):
        value = force_text(value)
        digits = len(DIGITS_RE.findall(value))
        plus_sign = len(PLUS_SIGN_RE.findall(value))
        hyphens = len(HYPHENS_RE.findall(value))
        spaces = len(SPACES_RE.findall(value))
        open_parentheses = len(OPEN_PARENTHESES.findall(value))
        close_parentheses = len(CLOSE_PARENTHESES.findall(value))
        slashes = len(SLASHES.findall(value))
        return (
            len(value) == (digits + plus_sign + hyphens + spaces
                           + open_parentheses + close_parentheses
                           + slashes)
            and digits >= 3
            and digits <= (15 if not plus_sign else 14)
            and hyphens + spaces <= digits / 2
            and open_parentheses == close_parentheses
            and open_parentheses <= 1
            and close_parentheses <= 1
            and slashes <= 1
        )

