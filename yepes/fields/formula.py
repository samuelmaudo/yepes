# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from django.db import models
from django.core.exceptions import ValidationError

from yepes.types import Formula


class FormulaField(models.CharField):

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('max_length', 255)
        self.variables = frozenset(kwargs.pop('variables', ()))
        super(FormulaField, self).__init__(*args, **kwargs)

    def contribute_to_class(self, cls, name):
        super(FormulaField, self).contribute_to_class(cls, name)
        setattr(cls, self.name, FormulaFieldDescriptor(self))

    def south_field_triple(self):
        """
        Returns a suitable description of this field for South.
        """
        from south.modelsinspector import introspector
        field_class = 'django.db.models.fields.CharField'
        args, kwargs = introspector(self)
        return (field_class, args, kwargs)

    def validate(self, value, model_instance):
        super(FormulaField, self).validate(value, model_instance)
        if not value:
            return
        try:
            f = Formula(value)
            if self.variables:
                f.calculate(**{v: 1 for v in self.variables})
        except SyntaxError as e:
            raise ValidationError('Invalid syntax: {0}'.format(e))


class FormulaFieldDescriptor(object):

    def __init__(self, field):
        self.value = '{0}_value'.format(field.name)

    def __get__(self, obj, cls=None):
        if obj is None:
            return self
        else:
            return obj.__dict__[self.value]

    def __set__(self, obj, value):
        if obj is None:
            raise AttributeError('Manager must be accessed via instance')
        elif value is None or isinstance(value, Formula):
            obj.__dict__[self.value] = value
        else:
            obj.__dict__[self.value] = Formula(value)

