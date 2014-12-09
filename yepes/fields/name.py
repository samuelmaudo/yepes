# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from django.db import models


class NameField(models.CharField):

    def clean(self, *args, **kwargs):
        value = super(NameField, self).clean(*args, **kwargs)
        if value is not None:
            value = ' '.join(value.split())

        return value

    def south_field_triple(self):
        from south.modelsinspector import introspector
        args, kwargs = introspector(self)
        return ('yepes.fields.NameField', args, kwargs)

