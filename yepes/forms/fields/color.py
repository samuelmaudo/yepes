# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from yepes.forms.fields.char import CharField
from yepes.validators import ColorValidator


class ColorField(CharField):

    default_validators = [ColorValidator()]

    def __init__(self, *args, **kwargs):
        kwargs['force_ascii'] = False
        kwargs['force_lower'] = False
        kwargs['force_upper'] = True
        kwargs['normalize_spaces'] = False
        kwargs['trim_spaces'] = True
        super(ColorField, self).__init__(*args, **kwargs)

    def to_python(self, *args, **kwargs):
        value = super(ColorField, self).to_python(*args, **kwargs)
        if value:

            if not value.startswith('#'):
                value = ''.join(('#', value))

            if len(value) == 4:
                value = ''.join((value, value[1:4]))

        return value

