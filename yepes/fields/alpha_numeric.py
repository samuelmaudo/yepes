# -*- coding:utf-8 -*-

from __future__ import unicode_literals

import re

from django.db import models

from yepes import forms

NON_ALNUM_RE = re.compile(r'[^0-9A-Za-z]')


class AlphaNumericField(models.CharField):

    def clean(self, *args, **kwargs):
        value = super(AlphaNumericField, self).clean(*args, **kwargs)
        if value is not None:
            value = NON_ALNUM_RE.sub('', value)

        return value

    def formfield(self, **kwargs):
        kwargs.setdefault('form_class', forms.AlphaNumericField)
        return super(AlphaNumericField, self).formfield(**kwargs)

    def south_field_triple(self):
        from south.modelsinspector import introspector
        args, kwargs = introspector(self)
        return ('yepes.fields.AlphaNumericField', args, kwargs)

