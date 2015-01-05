# -*- coding:utf-8 -*-

from __future__ import unicode_literals

import re

from django import forms

NON_ALNUM_RE = re.compile(r'[^0-9A-Za-z]')


class AlphaNumericField(forms.CharField):

    def to_python(self, value):
        value = super(AlphaNumericField, self).to_python(value)
        if value is None:
            return value
        else:
            return NON_ALNUM_RE.sub('', value)

