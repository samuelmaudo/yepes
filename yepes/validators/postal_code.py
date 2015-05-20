# -*- coding:utf-8 -*-

from __future__ import unicode_literals

import re

from django.utils.encoding import smart_str
from django.utils.translation import ugettext_lazy as _

from yepes.validators import BaseValidator


class PostalCodeValidator(BaseValidator):
    """
    Checks if the value is a valid postal code.
    """

    code = 'invalid_postal_code'
    message = _('Enter a valid postal code.')

    def __call__(self, value):
        value = smart_str(value)
        alpha = len(re.findall(r'[a-zA-Z]', value))
        digit = len(re.findall(r'[0-9]', value))
        alnum = alpha + digit
        hyphens = len(re.findall(r'\-', value))
        spaces = len(re.findall(r' ', value))
        valid_chars = alnum + hyphens + spaces
        if (len(value) != valid_chars
                or digit < 1
                or alnum < 3
                or alnum > 11
                or hyphens + spaces > (alnum / 2)):
            self.invalid(value)

