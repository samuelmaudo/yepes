# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _

from yepes import forms
from yepes.fields.char import CharField
from yepes.utils.deconstruct import clean_keywords
from yepes.validators import ColorValidator


class ColorField(CharField):

    default_validators = [ColorValidator()]
    description = _('Hexadecimal color')

    def __init__(self, *args, **kwargs):
        kwargs['force_ascii'] = False
        kwargs['force_lower'] = False
        kwargs['force_upper'] = True
        kwargs['max_length'] = 7
        kwargs['normalize_spaces'] = False
        kwargs['trim_spaces'] = True
        super(ColorField, self).__init__(*args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super(ColorField, self).deconstruct()
        path = path.replace('yepes.fields.color', 'yepes.fields')
        clean_keywords(self, kwargs, immutables=[
            'force_ascii',
            'force_lower',
            'force_upper',
            'max_length',
            'normalize_spaces',
            'trim_spaces',
        ])
        return name, path, args, kwargs

    def formfield(self, **kwargs):
        kwargs.setdefault('form_class', forms.ColorField)
        return super(ColorField, self).formfield(**kwargs)

    def to_python(self, *args, **kwargs):
        value = super(ColorField, self).to_python(*args, **kwargs)
        if value:

            if not value.startswith('#'):
                value = ''.join(('#', value))

            if len(value) == 4:
                value = ''.join((value, value[1:4]))

        return value

