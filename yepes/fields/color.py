# -*- coding:utf-8 -*-

from __future__ import unicode_literals

import re

from django.core import validators
from django.db import models
from django.forms import fields as form_fields

__all__ = ('ColorField', )

COLOR_RE = re.compile('^#?((?:[0-F]{3}){1,2})$', re.IGNORECASE)


class ColorField(models.CharField):

    default_validators = [validators.RegexValidator(regex=COLOR_RE)]

    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = 7
        super(ColorField, self).__init__(*args, **kwargs)

    def clean(self, *args, **kwargs):
        value = super(ColorField, self).clean(*args, **kwargs)
        value = value.upper()
        if not value.startswith('#'):
            value = ''.join(('#', value))

        if len(value) == 4:
            value = ''.join((value, value[1:4]))

        return value

    def formfield(self, **kwargs):
        kwargs.update({
            'form_class': form_fields.RegexField,
            'regex': COLOR_RE,
        })
        return super(ColorField, self).formfield(**kwargs)

    def south_field_triple(self):
        """
        Returns a suitable description of this field for South.
        """
        from south.modelsinspector import introspector
        args, kwargs = introspector(self)
        del kwargs['max_length']
        return ('yepes.fields.ColorField', args, kwargs)

