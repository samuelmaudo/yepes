# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from django import VERSION as DJANGO_VERSION
if DJANGO_VERSION >= (1, 8):
    from django.core import checks

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import connection
from django.db import models
from django.utils.translation import ugettext_lazy as _

from yepes.conf import settings
from yepes.fields.calculated import CalculatedField
from yepes.utils.properties import cached_property


class IntegerField(CalculatedField, models.IntegerField):

    description = _('Integer (4 bytes)')

    def __init__(self, *args, **kwargs):
        if not kwargs.get('null', False):
            kwargs.setdefault('default', 0)
        self.max_value = kwargs.pop('max_value', None)
        self.min_value = kwargs.pop('min_value', None)
        super(IntegerField, self).__init__(*args, **kwargs)
        if DJANGO_VERSION < (1, 8):
            if self.min_value is not None:
                self.validators.append(MinValueValidator(self.min_value))
            if self.max_value is not None:
                self.validators.append(MaxValueValidator(self.max_value))

    def check(self, **kwargs):
        errors = super(IntegerField, self).check(**kwargs)
        errors.extend(self._check_max_value_attribute(**kwargs))
        errors.extend(self._check_min_value_attribute(**kwargs))
        errors.extend(self._check_column_range(**kwargs))
        return errors

    def _check_column_range(self):
        errors = []
        min_allowed, max_allowed = self.column_range
        if (min_allowed is not None
                and isinstance(self.min_value, six.integer_types)
                and self.min_value < min_allowed):
            errors.append(checks.Error(
                "'min_value' cannot exceed the limits of the database column.",
                hint="Set 'min_value' to {0} or more.".format(min_allowed),
                obj=self,
                id='yepes.E141',
            ))
        if (max_allowed is not None
                and isinstance(self.max_value, six.integer_types)
                and self.max_value > max_allowed):
            errors.append(checks.Error(
                "'max_value' cannot exceed the limits of the database column.",
                hint="Set 'max_value' to {0} or less.".format(max_allowed),
                obj=self,
                id='yepes.E142',
            ))
        return errors

    def _check_max_value_attribute(self, **kwargs):
        if (self.max_value is not None
                and not isinstance(self.max_value, six.integer_types)):
            return [
                checks.Error(
                    "'max_value' must be None or an integer.",
                    hint=None,
                    obj=self,
                    id='yepes.E143',
                )
            ]
        else:
            return []

    def _check_min_value_attribute(self, **kwargs):
        if self.min_value is None:
            return []
        elif not isinstance(self.min_value, six.integer_types):
            return [
                checks.Error(
                    "'min_value' must be None or an integer.",
                    hint=None,
                    obj=self,
                    id='yepes.E144',
                )
            ]
        elif (isinstance(self.max_value, six.integer_types)
                and self.max_value < self.min_value):
            return [
                checks.Error(
                    "'min_value' cannot be greater than 'max_value'.",
                    hint="Decrease 'min_value' or increase 'max_value'.",
                    obj=self,
                    id='yepes.E145',
                )
            ]
        else:
            return []

    def deconstruct(self):
        name, path, args, kwargs = super(IntegerField, self).deconstruct()
        path = path.replace('yepes.fields.integer', 'yepes.fields')
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
        return super(IntegerField, self).formfield(**params)

    def get_internal_type(self):
        if self.min_value == 0:
            return 'PositiveIntegerField'
        else:
            return 'IntegerField'

    @cached_property
    def column_range(self):
        # A tuple of the (min_value, max_value) form representing the range of
        # the database column bound to the field.
        if DJANGO_VERSION >= (1, 8):
            return connection.ops.integer_field_range(self.get_internal_type())
        else:
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

    @cached_property
    def validators(self):
        # These validators can't be added at field initialization time since
        # they're based on values retrieved from `connection`.
        range_validators = []
        min_allowed, max_allowed = self.range
        if min_allowed is not None:
            range_validators.append(MinValueValidator(min_allowed))
        if max_allowed is not None:
            range_validators.append(MaxValueValidator(max_allowed))
        return super(IntegerField, self).validators + range_validators


class BigIntegerField(IntegerField):

    description = _('Big integer (8 bytes)')

    def get_internal_type(self):
        return 'BigIntegerField'


class SmallIntegerField(IntegerField):

    description = _('Small integer (2 bytes)')

    def get_internal_type(self):
        if self.min_value == 0:
            return 'PositiveSmallIntegerField'
        else:
            return 'SmallIntegerField'

