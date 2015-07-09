# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _

from yepes import forms
from yepes.fields.char import CharField
from yepes.types import Formula
from yepes.utils.deconstruct import clean_keywords
from yepes.validators import FormulaValidator


class FormulaField(CharField):

    description = _('Formula')

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('max_length', 255)
        kwargs.setdefault('normalize_spaces', False)
        kwargs.setdefault('trim_spaces', True)
        self.variables = list(kwargs.pop('variables', []))
        super(FormulaField, self).__init__(*args, **kwargs)
        self.validators.append(FormulaValidator(self.variables))

    def contribute_to_class(self, cls, name):
        super(FormulaField, self).contribute_to_class(cls, name)
        setattr(cls, self.name, FormulaFieldDescriptor(self))

    def deconstruct(self):
        name, path, args, kwargs = super(FormulaField, self).deconstruct()
        path = path.replace('yepes.fields.formula', 'yepes.fields')
        clean_keywords(self, kwargs, variables={
            'max_length': 255,
            'normalize_spaces': False,
            'trim_spaces': True,
            'variables': [],
        })
        return name, path, args, kwargs

    def formfield(self, **kwargs):
        kwargs.setdefault('form_class', forms.FormulaField)
        kwargs.setdefault('variables', self.variables)
        return super(CharField, self).formfield(**kwargs)


class FormulaFieldDescriptor(object):

    def __init__(self, field):
        self.cache_name = field.get_cache_name()

    def __get__(self, obj, cls=None):
        if obj is None:
            return self
        else:
            return obj.__dict__[self.cache_name]

    def __set__(self, obj, value):
        if obj is None:
            raise AttributeError('Manager must be accessed via instance')
        elif value is None or isinstance(value, Formula):
            obj.__dict__[self.cache_name] = value
        else:
            obj.__dict__[self.cache_name] = Formula(value)

