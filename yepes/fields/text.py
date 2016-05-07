# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from django.core import checks
from django.core.validators import MaxLengthValidator, MinLengthValidator
from django.db import models
from django.utils import six
from django.utils.encoding import force_text

from yepes import forms
from yepes.fields.calculated import CalculatedField
from yepes.utils.deconstruct import clean_keywords


class TextField(CalculatedField, models.TextField):

    def __init__(self, *args, **kwargs):
        self.min_length = kwargs.pop('min_length', None)
        super(TextField, self).__init__(*args, **kwargs)
        if self.max_length is not None:
            self.validators.append(MaxLengthValidator(self.max_length))
        if self.min_length is not None:
            self.validators.append(MinLengthValidator(self.min_length))

    def check(self, **kwargs):
        errors = super(TextField, self).check(**kwargs)
        errors.extend(self._check_max_length_attribute(**kwargs))
        errors.extend(self._check_min_length_attribute(**kwargs))
        return errors

    def _check_max_length_attribute(self, **kwargs):
        if (self.max_length is not None
                and (not isinstance(self.max_length, six.integer_types)
                        or self.max_length <= 0)):
            return [
                checks.Error(
                    "'max_length' must be None or a positive integer.",
                    hint=None,
                    obj=self,
                    id='yepes.E151',
                )
            ]
        else:
            return []

    def _check_min_length_attribute(self, **kwargs):
        if self.min_length is None:
            return []
        elif (not isinstance(self.min_length, six.integer_types)
                or self.min_length <= 0):
            return [
                checks.Error(
                    "'min_length' must be None or a positive integer.",
                    hint=None,
                    obj=self,
                    id='yepes.E152',
                )
            ]
        elif (isinstance(self.max_length, six.integer_types)
                and self.max_length < self.min_length):
            return [
                checks.Error(
                    "'min_length' cannot be greater than 'max_length'.",
                    hint="Decrease 'min_length' or increase 'max_length'.",
                    obj=self,
                    id='yepes.E153',
                )
            ]
        else:
            return []

    def deconstruct(self):
        name, path, args, kwargs = super(TextField, self).deconstruct()
        path = path.replace('yepes.fields.text', 'yepes.fields')
        clean_keywords(self, kwargs, variables={
            'min_length': None,
        })
        return (name, path, args, kwargs)

    def formfield(self, **kwargs):
        params = {
            'form_class': forms.TextField,
            'max_length': self.max_length,
            'min_length': self.min_length,
        }
        params.update(kwargs)
        return models.Field.formfield(self, **params)

    def to_python(self, value):
        if value is None or isinstance(value, six.string_types):
            return value
        else:
            return force_text(value)

