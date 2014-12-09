# -*- coding:utf-8 -*-

from __future__ import unicode_literals

import re

from django.utils.encoding import smart_bytes
from django.utils.translation import ugettext_lazy as _

from yepes.validators import BaseValidator


class PostalCodeValidator(BaseValidator):
    """
    Checks if the value is a valid postal code.
    """

    code = 'invalid_postal_code'
    message = _('Enter a valid postal code.')

    def __call__(self, value):
        value = smart_bytes(value)
        alnum = len(re.findall(r'[a-zA-Z0-9]', value))
        hyphens = len(re.findall(r'\-', value))
        spaces = len(re.findall(r' ', value))
        valid_chars = (alnum + hyphens + spaces)
        if (len(value) != valid_chars
                or alnum < 3
                or alnum > 11
                or hyphens + spaces > (alnum / 2)):
            self.invalid(value)

