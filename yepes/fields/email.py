# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _

from yepes import forms
from yepes.fields.char import CharField
from yepes.utils.deconstruct import clean_keywords
from yepes.utils.emails import normalize_email
from yepes.validators import RestrictedEmailValidator


class EmailField(CharField):

    default_validators = [RestrictedEmailValidator()]
    description = _('Email address')

    def __init__(self, *args, **kwargs):
        kwargs['force_ascii'] = False
        kwargs['force_lower'] = False
        kwargs['force_upper'] = False
        kwargs.setdefault('max_length', 63)
        kwargs['normalize_spaces'] = False
        kwargs['trim_spaces'] = False
        super(EmailField, self).__init__(*args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super(EmailField, self).deconstruct()
        path = path.replace('yepes.fields.email', 'yepes.fields')
        clean_keywords(self, kwargs, variables={
            'max_length': 63,
        }, constants=[
            'force_ascii',
            'force_lower',
            'force_upper',
            'normalize_spaces',
            'trim_spaces',
        ])
        return name, path, args, kwargs

    def formfield(self, **kwargs):
        kwargs.setdefault('form_class', forms.EmailField)
        return super(EmailField, self).formfield(**kwargs)

    def to_python(self, *args, **kwargs):
        value = super(EmailField, self).to_python(*args, **kwargs)
        if value is None:
            return value
        else:
            return normalize_email(value)

