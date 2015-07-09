# -*- coding:utf-8 -*-

from __future__ import unicode_literals

import re

from django.utils import six
from django.utils.translation import ugettext_lazy as _

from yepes import forms
from yepes.fields.calculated import CalculatedSubfield
from yepes.fields.char import CharField
from yepes.utils.deconstruct import clean_keywords


class CommaSeparatedField(CalculatedSubfield, CharField):

    description = _('Comma-separated strings')

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('max_length', 255)
        kwargs['normalize_spaces'] = False
        self.separator = kwargs.pop('separator', ', ')
        self.separator_re = re.compile(
            '\s*{0}\s*'.format(re.escape(self.separator.strip())),
            re.UNICODE,
        )
        kwargs['trim_spaces'] = False
        super(CommaSeparatedField, self).__init__(*args, **kwargs)

    def clean(self, value, model_instance):
        value = self.get_prep_value(value)
        self.validate(value, model_instance)
        self.run_validators(value)
        return self.to_python(value)

    def deconstruct(self):
        name, path, args, kwargs = super(CommaSeparatedField, self).deconstruct()
        path = path.replace('yepes.fields.comma_separated', 'yepes.fields')
        clean_keywords(self, kwargs, variables={
            'max_length': 255,
            'separator': ', ',
        }, constants=[
            'normalize_spaces',
            'trim_spaces',
        ])
        return name, path, args, kwargs

    def formfield(self, **kwargs):
        kwargs.setdefault('form_class', forms.CommaSeparatedField)
        kwargs.setdefault('separator', self.separator)
        return super(CommaSeparatedField, self).formfield(**kwargs)

    def get_prep_value(self, value):
        if value is None or isinstance(value, six.string_types):
            return value
        else:
            return self.separator.join(value)

    def to_python(self, value):
        if value is None:
            return value
        elif not value:
            return []
        elif isinstance(value, six.string_types):
            return self.separator_re.split(value)
        else:
            return list(value)

    def value_to_string(self, obj):
        value = self._get_val_from_obj(obj)
        return self.get_prep_value(value)

