# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from django import forms


class NameField(forms.CharField):

    def to_python(self, value):
        value = super(NameField, self).to_python(value)
        if value is None:
            return value
        else:
            return ' '.join(value.split())

