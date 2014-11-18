# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from django import forms
from django.core.validators import validate_email

from yepes.utils.email import normalize_email


class EmailField(forms.CharField):
    widget = forms.EmailInput
    default_validators = [validate_email]

    def to_python(self, value):
        if value in self.empty_values:
            return ''
        else:
            return normalize_email(value)

