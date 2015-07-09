# -*- coding:utf-8 -*-

from __future__ import unicode_literals

import re

from django.utils import six

from yepes.forms.fields.char import CharField


class CommaSeparatedField(CharField):

    def __init__(self, *args, **kwargs):
        kwargs['normalize_spaces'] = False
        self.separator = kwargs.pop('separator', ', ')
        self.separator_re = re.compile(
            '\s*{0}\s*'.format(re.escape(self.separator.strip())),
            re.UNICODE,
        )
        kwargs['trim_spaces'] = True
        super(CommaSeparatedField, self).__init__(*args, **kwargs)

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
        elif isinstance(value, six.string_types):
            return value
        else:
            return self.separator.join(value)

