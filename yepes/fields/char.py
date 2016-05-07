# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from django.core import checks
from django.core.validators import MinLengthValidator
from django.db import models
from django.utils import six
from django.utils.encoding import force_text
from django.utils.translation import ugettext_lazy as _

from yepes import forms
from yepes.fields.calculated import CalculatedField
from yepes.utils import unidecode
from yepes.utils.deconstruct import clean_keywords
from yepes.validators import CharSetValidator


class CharField(CalculatedField, models.CharField):

    description = _('String')

    def __init__(self, *args, **kwargs):
        self.charset = kwargs.pop('charset', None)
        self.force_ascii = kwargs.pop('force_ascii', False)
        self.force_lower = kwargs.pop('force_lower', False)
        self.force_upper = kwargs.pop('force_upper', False)
        self.min_length = kwargs.pop('min_length', None)
        self.normalize_spaces = kwargs.pop('normalize_spaces', True)
        self.trim_spaces = kwargs.pop('trim_spaces', False)
        super(CharField, self).__init__(*args, **kwargs)
        if self.min_length is not None:
            self.validators.append(MinLengthValidator(self.min_length))
        if self.charset is not None:
            self.validators.append(CharSetValidator(self.charset))

    def check(self, **kwargs):
        errors = super(CharField, self).check(**kwargs)
        errors.extend(self._check_min_length_attribute(**kwargs))
        return errors

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
                    id='yepes.E111',
                )
            ]
        elif (isinstance(self.max_length, six.integer_types)
                and self.max_length < self.min_length):
            return [
                checks.Error(
                    "'min_length' cannot be greater than 'max_length'.",
                    hint="Decrease 'min_length' or increase 'max_length'.",
                    obj=self,
                    id='yepes.E112',
                )
            ]
        else:
            return []

    def deconstruct(self):
        name, path, args, kwargs = super(CharField, self).deconstruct()
        path = path.replace('yepes.fields.char', 'yepes.fields')
        clean_keywords(self, kwargs, variables={
            'charset': None,
            'force_ascii': False,
            'force_lower': False,
            'force_upper': False,
            'min_length': None,
            'normalize_spaces': True,
            'trim_spaces': False,
        })
        return (name, path, args, kwargs)

    def formfield(self, **kwargs):
        params = {
            'form_class': forms.CharField,
            'charset': self.charset,
            'force_ascii': self.force_ascii,
            'force_lower': self.force_lower,
            'force_upper': self.force_upper,
            'max_length': self.max_length,
            'min_length': self.min_length,
            'normalize_spaces': self.normalize_spaces,
            'trim_spaces': self.trim_spaces,
        }
        params.update(kwargs)
        return super(CharField, self).formfield(**params)

    def to_python(self, value):
        if value is None:
            return value

        if not isinstance(value, six.string_types):
            value = force_text(value)

        if self.normalize_spaces:
            value = ' '.join(value.split())
        elif self.trim_spaces:
            value = value.strip()

        if not value:
            return value

        if self.force_ascii:
            value = unidecode(value)

        if self.force_lower:
            value = value.lower()
        elif self.force_upper:
            value = value.upper()

        return value

