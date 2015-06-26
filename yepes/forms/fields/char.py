# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from django import forms

from yepes.utils import unidecode
from yepes.validators import CharSetValidator


class CharField(forms.CharField):

    def __init__(self, *args, **kwargs):
        self.charset = kwargs.pop('charset', None)
        self.force_ascii = kwargs.pop('force_ascii', False)
        self.force_lower = kwargs.pop('force_lower', False)
        self.force_upper = kwargs.pop('force_upper', False)
        self.normalize_spaces = kwargs.pop('normalize_spaces', True)
        self.trim_spaces = kwargs.pop('trim_spaces', False)
        super(CharField, self).__init__(*args, **kwargs)
        if self.charset is not None:
            self.validators.append(CharSetValidator(self.charset))

    def to_python(self, *args, **kwargs):
        value = super(CharField, self).to_python(*args, **kwargs)
        if value:

            if self.force_ascii:
                value = unidecode(value)

            if self.force_lower:
                value = value.lower()
            elif self.force_upper:
                value = value.upper()

            if self.normalize_spaces:
                value = ' '.join(value.split())
            elif self.trim_spaces:
                value = value.strip()

        return value

