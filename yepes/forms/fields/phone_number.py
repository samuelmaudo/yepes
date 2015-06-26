# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from yepes.forms.fields.char import CharField
from yepes.validators import PhoneNumberValidator


class PhoneNumberField(CharField):

    default_validators = [PhoneNumberValidator()]

    def __init__(self, *args, **kwargs):
        kwargs['force_lower'] = False
        kwargs['force_upper'] = False
        kwargs['normalize_spaces'] = True
        kwargs['trim_spaces'] = False
        super(PhoneNumberField, self).__init__(*args, **kwargs)

