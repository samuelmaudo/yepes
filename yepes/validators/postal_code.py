# -*- coding:utf-8 -*-

from __future__ import unicode_literals

import re

from django.utils.encoding import force_text
from django.utils.translation import ugettext_lazy as _

from yepes.validators.base import Validator

LETTERS_RE = re.compile(r'[A-Z]', re.IGNORECASE)
DIGITS_RE = re.compile(r'[0-9]')
HYPHENS_RE = re.compile(r'-')
SPACES_RE = re.compile(r' ')


class PostalCodeValidator(Validator):
    """
    Checks if the value is a valid postal code.
    """
    message = _('Enter a valid postal code.')

    def validate(self, value):
        value = force_text(value)
        letters = len(LETTERS_RE.findall(value))
        digits = len(DIGITS_RE.findall(value))
        letters_and_digits = letters + digits
        hyphens = len(HYPHENS_RE.findall(value))
        spaces = len(SPACES_RE.findall(value))
        hyphens_and_spaces = hyphens + spaces
        return (
            len(value) == letters_and_digits + hyphens_and_spaces
            and digits >= 1
            and letters_and_digits >= 3
            and letters_and_digits <= 11
            and hyphens_and_spaces <= letters_and_digits / 2
        )

