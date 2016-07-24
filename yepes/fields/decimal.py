# -*- coding:utf-8 -*-

from __future__ import absolute_import, unicode_literals

from decimal import Decimal as dec

from django.core import checks
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import six

from yepes.conf import settings
from yepes.fields.calculated import CalculatedField
from yepes.utils.deconstruct import clean_keywords
from yepes.utils.properties import cached_property

DECIMAL_FIELD_RANGES = {
    (6, 2): dec('9999.99')
}

class DecimalField(CalculatedField, models.DecimalField):

    def __init__(self, *args, **kwargs):
        if not kwargs.get('null', False):
            kwargs.setdefault('default', dec('0'))
        self.max_value = kwargs.pop('max_value', None)
        self.min_value = kwargs.pop('min_value', None)
        super(DecimalField, self).__init__(*args, **kwargs)
        min_allowed, max_allowed = self.range
        self.validators.append(MinValueValidator(min_allowed))
        self.validators.append(MaxValueValidator(max_allowed))

    def check(self, **kwargs):
        errors = super(DecimalField, self).check(**kwargs)
        errors.extend(self._check_max_value_attribute(**kwargs))
        errors.extend(self._check_min_value_attribute(**kwargs))
        errors.extend(self._check_column_range())
        return errors

    def _check_column_range(self):
        errors = []
        if (isinstance(self.max_digits, six.integer_types)
                and isinstance(self.decimal_places, six.integer_types)):
            min_allowed, max_allowed = self.column_range
            if (isinstance(self.min_value, dec)
                    and self.min_value < min_allowed):
                errors.append(checks.Error(
                    "'min_value' cannot exceed the limits of the database column.",
                    hint="Set 'min_value' to {0} or more.".format(min_allowed),
                    obj=self,
                    id='yepes.E121',
                ))
            if (isinstance(self.max_value, dec)
                    and self.max_value > max_allowed):
                errors.append(checks.Error(
                    "'max_value' cannot exceed the limits of the database column.",
                    hint="Set 'max_value' to {0} or less.".format(max_allowed),
                    obj=self,
                    id='yepes.E122',
                ))
        return errors

    def _check_max_value_attribute(self, **kwargs):
        if (self.max_value is not None
                and not isinstance(self.max_value, dec)):
            return [
                checks.Error(
                    "'max_value' must be None or a decimal.",
                    hint=None,
                    obj=self,
                    id='yepes.E123',
                )
            ]
        else:
            return []

    def _check_min_value_attribute(self, **kwargs):
        if self.min_value is None:
            return []
        elif not isinstance(self.min_value, dec):
            return [
                checks.Error(
                    "'min_value' must be None or a decimal.",
                    hint=None,
                    obj=self,
                    id='yepes.E124',
                )
            ]
        elif (isinstance(self.max_value, dec)
                and self.max_value < self.min_value):
            return [
                checks.Error(
                    "'min_value' cannot be greater than 'max_value'.",
                    hint="Decrease 'min_value' or increase 'max_value'.",
                    obj=self,
                    id='yepes.E125',
                )
            ]
        else:
            return []

    def deconstruct(self):
        name, path, args, kwargs = super(DecimalField, self).deconstruct()
        path = path.replace('yepes.fields.decimal', 'yepes.fields')
        clean_keywords(self, kwargs, variables={
            'max_value': None,
            'min_value': None,
        })
        return (name, path, args, kwargs)

    def formfield(self, **kwargs):
        params = {
            'localize': settings.USE_L10N, # It is not necessary to pass the
            'max_value': self.max_value,   # column range because the form
            'min_value': self.min_value,   # field checks it carefully.
        }
        params.update(kwargs)
        return super(DecimalField, self).formfield(**params)

    @cached_property
    def column_range(self):
        # A tuple of the (min_value, max_value) form representing the range
        # of the database column bound to the field.
        key = (self.max_digits, self.decimal_places)
        max_value = DECIMAL_FIELD_RANGES.get(key)
        if max_value is None:
            digits = '9' * self.max_digits
            decimals = '1' + ('0' * self.decimal_places)
            max_value = DECIMAL_FIELD_RANGES[key] = dec(digits) / dec(decimals)

        return (-max_value, max_value)

    @cached_property
    def range(self):
        # A tuple of the (min_value, max_value) form representing the range of
        # the field.
        min_allowed, max_allowed = self.column_range
        if self.min_value is not None:
            min_allowed = self.min_value
        if self.max_value is not None:
            max_allowed = self.max_value
        return (min_allowed, max_allowed)

