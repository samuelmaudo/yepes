# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _

from yepes import forms
from yepes.fields.char import CharField
from yepes.utils.deconstruct import clean_keywords
from yepes.validators import IdentifierValidator


class IdentifierField(CharField):

    default_validators = [IdentifierValidator()]
    description = _('Identifier')

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('db_index', True)
        kwargs.setdefault('max_length', 31)
        kwargs.setdefault('min_length', 1)
        kwargs['normalize_spaces'] = False
        kwargs['trim_spaces'] = True
        kwargs.setdefault('unique', True)
        super(IdentifierField, self).__init__(*args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super(IdentifierField, self).deconstruct()
        path = path.replace('yepes.fields.key', 'yepes.fields')
        clean_keywords(self, kwargs, variables={
            'db_index': True,
            'max_length': 31,
            'min_length': 1,
            'unique': True,
        }, constants=[
            'normalize_spaces',
            'trim_spaces',
        ])
        return name, path, args, kwargs

    def formfield(self, **kwargs):
        kwargs.setdefault('form_class', forms.IdentifierField)
        return super(IdentifierField, self).formfield(**kwargs)

