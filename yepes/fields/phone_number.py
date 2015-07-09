# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _

from yepes import forms
from yepes.fields.char import CharField
from yepes.validators import PhoneNumberValidator
from yepes.utils.deconstruct import clean_keywords


class PhoneNumberField(CharField):

    default_validators = [PhoneNumberValidator()]
    description = _('Generic phone number')

    def __init__(self, *args, **kwargs):
        kwargs['force_lower'] = False
        kwargs['force_upper'] = False
        kwargs.setdefault('max_length', 31)
        kwargs['normalize_spaces'] = True
        kwargs['trim_spaces'] = False
        super(PhoneNumberField, self).__init__(*args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super(PhoneNumberField, self).deconstruct()
        path = path.replace('yepes.fields.phone_number', 'yepes.fields')
        clean_keywords(self, kwargs, variables={
            'max_length': 31,
        }, constants=[
            'force_lower',
            'force_upper',
            'normalize_spaces',
            'trim_spaces',
        ])
        return name, path, args, kwargs

    def formfield(self, **kwargs):
        kwargs.setdefault('form_class', forms.PhoneNumberField)
        return super(PhoneNumberField, self).formfield(**kwargs)

