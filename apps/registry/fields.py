# -*- coding:utf-8 -*-

from __future__ import unicode_literals

import importlib
import re

from django import forms
from django.forms.fields import (
    Field,
    BooleanField, NullBooleanField,
    CharField, RegexField,
    DateField, TimeField, SplitDateTimeField as DateTimeField,
    IntegerField, FloatField, DecimalField,
    EmailField, URLField, GenericIPAddressField as IPAddressField,
)
from django.utils import six
from django.utils.encoding import force_text, smart_text
from django.utils.functional import SimpleLazyObject

from yepes.apps.registry import utils
from yepes.forms.fields import CommaSeparatedField

__all__ = (
    'Field', 'BooleanField', 'CharField', 'ChoiceField', 'CommaSeparatedField',
    'DateField', 'DateTimeField', 'DecimalField', 'EmailField', 'FloatField',
    'IntegerField', 'IPAddressField', 'ModelChoiceField', 'ModuleField',
    'NullBooleanField', 'PasswordField', 'RegexField', 'TextField',
    'TimeField', 'URLField',
)


class ChoiceField(forms.TypedChoiceField):

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('coerce', smart_text)
        super(ChoiceField, self).__init__(*args, **kwargs)

    @property
    def is_long(self):
        for choice, verbose in self.choices:
            if len(force_text(choice)) > 255:
                return True
        else:
            return False


class ModelChoiceField(forms.ModelChoiceField):

    def __init__(self, queryset=None, *args, **kwargs):
        if not queryset:
            model = kwargs.pop('model')
            queryset = SimpleLazyObject(lambda: utils.get_queryset(model))
        super(ModelChoiceField, self).__init__(queryset, *args, **kwargs)

    def to_python(self, value):
        if isinstance(value, self.queryset.model):
            return value
        else:
            return super(ModelChoiceField, self).to_python(value)

    def value_to_string(self, value):
        return self.prepare_value(value)


class ModuleField(forms.CharField):

    def prepare_value(self, value):
        return self.value_to_string(value)

    def to_python(self, value):
        if not value:
            return None
        elif isinstance(value, six.string_types):
            return importlib.import_module(value)
        else:
            return value

    def value_to_string(self, value):
        if not value:
            return ''
        elif not isinstance(value, six.string_types):
            return getattr(value, '__name__', '')
        else:
            return value


class PasswordField(forms.CharField):
    widget = forms.PasswordInput


class TextField(forms.CharField):
    is_long = True
    widget = forms.Textarea

