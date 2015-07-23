# -*- coding:utf-8 -*-

from __future__ import unicode_literals

#from django.core import checks
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from yepes.conf import settings
from yepes.fields.calculated import CalculatedField
from yepes.utils.deconstruct import clean_keywords
from yepes.utils.properties import cached_property


class FloatField(CalculatedField, models.FloatField):

    def __init__(self, *args, **kwargs):
        if not kwargs.get('null', False):
            kwargs.setdefault('default', 0.0)
        self.max_value = kwargs.pop('max_value', None)
        self.min_value = kwargs.pop('min_value', None)
        super(FloatField, self).__init__(*args, **kwargs)
        if self.min_value is not None:
            self.validators.append(MinValueValidator(self.min_value))
        if self.max_value is not None:
            self.validators.append(MaxValueValidator(self.max_value))

    def check(self, **kwargs):
        errors = super(FloatField, self).check(**kwargs)
        errors.extend(self._check_max_value_attribute(**kwargs))
        errors.extend(self._check_min_value_attribute(**kwargs))
        return errors

    def _check_max_value_attribute(self, **kwargs):
        if (self.max_value is not None
                and not isinstance(self.max_value, float)):
            return [
                checks.Error(
                    "'max_value' must be None or a float.",
                    hint=None,
                    obj=self,
                    id='yepes.E131',
                )
            ]
        else:
            return []

    def _check_min_value_attribute(self, **kwargs):
        if self.min_value is None:
            return []
        elif not isinstance(self.min_value, float):
            return [
                checks.Error(
                    "'min_value' must be None or a float.",
                    hint=None,
                    obj=self,
                    id='yepes.E132',
                )
            ]
        elif (isinstance(self.max_value, float)
                and self.max_value < self.min_value):
            return [
                checks.Error(
                    "'min_value' cannot be greater than 'max_value'.",
                    hint="Decrease 'min_value' or increase 'max_value'.",
                    obj=self,
                    id='yepes.E133',
                )
            ]
        else:
            return []

    def deconstruct(self):
        name, path, args, kwargs = super(FloatField, self).deconstruct()
        path = path.replace('yepes.fields.float', 'yepes.fields')
        clean_keywords(self, kwargs, variables={
            'max_value': None,
            'min_value': None,
        })
        return (name, path, args, kwargs)

    def formfield(self, **kwargs):
        params = {
            'localize': settings.USE_L10N,
            'max_value': self.range[1],
            'min_value': self.range[0],
        }
        params.update(kwargs)
        return super(FloatField, self).formfield(**params)

    @cached_property
    def column_range(self):
        # A tuple of the (min_value, max_value) form representing the range of
        # the database column bound to the field.
        return (None, None)

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

