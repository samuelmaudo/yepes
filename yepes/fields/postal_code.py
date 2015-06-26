# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _

from yepes import forms
from yepes.fields.char import CharField
from yepes.validators import PostalCodeValidator
from yepes.utils.deconstruct import clean_keywords


class PostalCodeField(CharField):

    default_validators = [PostalCodeValidator()]
    description = _('Generic postal code')

    def __init__(self, *args, **kwargs):
        kwargs['force_lower'] = False
        kwargs['force_upper'] = True
        kwargs.setdefault('max_length', 15)
        kwargs['normalize_spaces'] = True
        kwargs['trim_spaces'] = False
        super(PostalCodeField, self).__init__(*args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super(PostalCodeField, self).deconstruct()
        path = path.replace('yepes.fields.postal_code', 'yepes.fields')
        clean_keywords(self, kwargs, defaults={
            'max_length': 15,
        }, immutables=[
            'force_lower',
            'force_upper',
            'normalize_spaces',
            'trim_spaces',
        ])
        return name, path, args, kwargs

    def formfield(self, **kwargs):
        kwargs.setdefault('form_class', forms.PostalCodeField)
        return super(PostalCodeField, self).formfield(**kwargs)

