# -*- coding:utf-8 -*-

from __future__ import unicode_literals

import re

from django.utils.encoding import force_text
from django.utils.translation import ugettext_lazy as _

from yepes.validators.base import Validator


class PostalCodeValidator(Validator):
    """
    Checks if the value is a valid postal code.
    """
    message = _('Enter a valid postal code.')

    def validate(self, value):
        value = force_text(value)
        alpha = len(re.findall(r'[a-zA-Z]', value))
        digit = len(re.findall(r'[0-9]', value))
        alnum = alpha + digit
        hyphens = len(re.findall(r'\-', value))
        spaces = len(re.findall(r' ', value))
        valid_chars = alnum + hyphens + spaces
        return (
            len(value) == (alnum + hyphens + spaces)
            and digit >= 1
            and alnum >= 3
            and alnum <= 11
            and hyphens + spaces <= (alnum / 2)
        )

