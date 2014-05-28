# -*- coding:utf-8 -*-

from __future__ import unicode_literals

import re

from django.db import models
from django.utils import six

from yepes import forms


@six.add_metaclass(models.SubfieldBase)
class CommaSeparatedField(models.CharField):

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('max_length', 255)
        self.separator = kwargs.pop('separator', ', ')
        self.separator_re = re.compile(
                '\s*{0}\s*'.format(re.escape(self.separator.strip())),
                re.UNICODE)
        super(CommaSeparatedField, self).__init__(*args, **kwargs)

    def clean(self, value, model_instance):
        value = self.get_prep_value(value)
        self.validate(value, model_instance)
        self.run_validators(value)
        return self.to_python(value)

    def formfield(self, **kwargs):
        kwargs.setdefault('form_class', forms.CommaSeparatedField)
        kwargs.setdefault('separator', self.separator)
        return super(CommaSeparatedField, self).formfield(**kwargs)

    def get_prep_value(self, value):
        if isinstance(value, (list, tuple)):
            value = self.separator.join(value)
        return value

    def south_field_triple(self):
        """
        Returns a suitable description of this field for South.
        """
        from south.modelsinspector import introspector
        field_class = 'django.db.models.fields.CharField'
        args, kwargs = introspector(self)
        return (field_class, args, kwargs)

    def to_python(self, value):
        if not value:
            if value is not None:
                value = []
        elif not isinstance(value, (list, tuple)):
            value = self.separator_re.split(value)
        return value

    def value_to_string(self, obj):
        value = self._get_val_from_obj(obj)
        return self.get_prep_value(value)

