# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from django.forms import EmailInput

from yepes.forms.fields.char import CharField
from yepes.utils.emails import normalize_email
from yepes.validators import RestrictedEmailValidator


class EmailField(CharField):

    default_validators = [RestrictedEmailValidator()]
    widget = EmailInput

    def __init__(self, *args, **kwargs):
        kwargs['force_ascii'] = False
        kwargs['force_lower'] = False
        kwargs['force_upper'] = False
        kwargs['normalize_spaces'] = False
        kwargs['trim_spaces'] = False
        super(EmailField, self).__init__(*args, **kwargs)

    def to_python(self, *args, **kwargs):
        value = super(EmailField, self).to_python(*args, **kwargs)
        if value:
            return normalize_email(value)
        else:
            return value

