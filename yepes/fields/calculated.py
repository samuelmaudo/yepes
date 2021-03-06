# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from django.core import checks
from django.core.exceptions import ImproperlyConfigured

from yepes.types import Undefined
from yepes.utils.deconstruct import clean_keywords


class CalculatedField(object):

    def __init__(self, *args, **kwargs):
        self.calculated = kwargs.pop('calculated', False)
        if self.calculated:
            kwargs['editable'] = False
        super(CalculatedField, self).__init__(*args, **kwargs)

    def check(self, **kwargs):
        errors = super(CalculatedField, self).check(**kwargs)
        errors.extend(self._check_calculator())
        return errors

    def _check_calculator(self):
        calculator_name = self.get_calculator_name()
        calculator = getattr(self.model, calculator_name, None)
        if self.calculated and not callable(calculator):
            return [
                checks.Error(
                    'Calculated fields require defining a calculator method '
                    'in their model.',
                    hint="Define a method called '{0}' in model '{1}'".format(
                                calculator_name, self.model._meta.object_name),
                    obj=self,
                    id='yepes.E101',
                )
            ]
        else:
            return []

    def contribute_to_class(self, cls, name, **kwargs):
        super(CalculatedField, self).contribute_to_class(cls, name, **kwargs)
        if self.calculated:
            setattr(cls, self.name, CalculatedFieldDescriptor(self))

    def deconstruct(self):
        name, path, args, kwargs = super(CalculatedField, self).deconstruct()
        clean_keywords(self, kwargs, variables={
            'calculated': False,
        })
        return (name, path, args, kwargs)

    def get_calculator_name(self):
        return 'calculate_{0}'.format(self.name)

    def get_default(self):
        if self.calculated:
            return Undefined
        else:
            return super(CalculatedField, self).get_default()

    def has_default(self):
        if self.calculated:
            return False
        else:
            return super(CalculatedField, self).has_default()


class CalculatedFieldDescriptor(object):

    def __init__(self, field):
        self.field = field
        self.calculator_name = field.get_calculator_name()

    def __get__(self, obj, cls=None):
        if obj is None:
            return self

        try:
            value = obj.__dict__[self.field.attname]
        except KeyError:
            name = self.calculator_name
            try:
                calculator = getattr(obj, name)
            except AttributeError:
                # We do not raise an AttributeError because it
                # would be hidden by ``__getattr__()``.
                args = (obj.__class__.__name__, name)
                msg = "'{0}' object has no method '{1}'"
                raise ImproperlyConfigured(msg.format(*args))
            else:
                value = calculator()
                self.__set__(obj, value)

        return value

    def __set__(self, obj, value):
        if value is not Undefined:
            obj.__dict__[self.field.attname] = value

