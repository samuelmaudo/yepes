# -*- coding:utf-8 -*-

from __future__ import unicode_literals

import re

from django import forms
from django.utils import six


class CommaSeparatedField(forms.CharField):

    def __init__(self, *args, **kwargs):
        separator = kwargs.pop('separator', ', ')
        regex = '\s*{0}\s*'.format(re.escape(separator.strip()))
        super(CommaSeparatedField, self).__init__(*args, **kwargs)
        self.separator_re = re.compile(regex, re.UNICODE)
        self.separator = separator

    def clean(self, value):
        value = self.prepare_value(value)
        self.validate(value)
        self.run_validators(value)
        return self.to_python(value)

    def prepare_value(self, value):
        return self.value_to_string(value)

    def to_python(self, value):
        if not value and value is not None:
            return []
        elif isinstance(value, six.string_types):
            return self.separator_re.split(value)
        else:
            return value

    def value_to_string(self, value):
        """
        This method is for use field into ``yepes.apps.registry``.
        """
        if not value:
            return ''
        elif not isinstance(value, six.string_types):
            return self.separator.join(value)
        else:
            return value

