# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from django.utils import six
from django.utils.encoding import force_str, force_text
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext as _

from yepes.exceptions import MissingAttributeError


@python_2_unicode_compatible
class Bit(object):

    def __new__(cls, value=None, field=None):
        self = object.__new__(cls)
        self._field = field
        self._value = int(value or 0)
        return self

    def __getattr__(self, name):
        if name.startswith('_'):
            raise MissingAttributeError(self, name)
        else:
            return (self._value & getattr(self._field.flags, name))

    def __repr__(self):
        args = (
            self.__class__.__name__,
            bin(self._value)[2:],
        )
        return force_str('<{0}: {1}>'.format(*args))

    def __str__(self):
        if not self._field:
            return force_text(bin(self._value)[2:])
        elif not self._value:
            return _('(All)')
        else:
            verbose_names = self._field.flags.iter_verbose_names(self._value)
            return ', '.join(force_text(n) for n in verbose_names)

    def __bool__(self):
        return bool(self._value)

    def __int__(self):
        return self._value

    def __nonzero__(self):
        return self.__bool__()

    def __eq__(self, other):
        if self._field:
            return (self._field.flags.get_value(other) == self._value)
        elif isinstance(other, Bit):
            return (other._field == self._field and other._value == self._value)
        elif isinstance(other, six.integer_types):
            return (other == self._value)
        else:
            msg = 'Bit object or integer was expected, {0!r} received'
            raise TypeError(msg.format(other))

    def __ne__(self, other):
        return (not self.__eq__(other))

    def __and__(self, other):
        if isinstance(other, Bit):
            assert other._field == self._field
            other = other._value
        return self.__class__(other & self._value, self._field)

    def __rand__(self, other):
        if isinstance(other, Bit):
            assert other._field == self._field
            other = other._value
        return self.__class__(self._value & other, self._field)

    def __or__(self, other):
        if isinstance(other, Bit):
            assert other._field == self._field
            other = other._value
        return self.__class__(other | self._value, self._field)

    def __ror__(self, other):
        if isinstance(other, Bit):
            assert other._field == self._field
            other = other._value
        return self.__class__(self._value | other, self._field)

    def __xor__(self, other):
        if isinstance(other, Bit):
            assert other._field == self._field
            other = other._value
        return self.__class__(other ^ self._value, self._field)

    def __rxor__(self, other):
        if isinstance(other, Bit):
            assert other._field == self._field
            other = other._value
        return self.__class__(self._value ^ other, self._field)

    def __invert__(self):
        if self._field:
            max_value = self._field.flags.get_max_value()
        else:
            max_value = (2 ** (len(bin(self._value)) - 2)) - 1
        return self.__class__(self._value ^ max_value, self._field)

    def __getstate__(self):
        return {
            'app': self._field.model._meta.app_label,
            'field': self._field.name,
            'model': self._field.model._meta.object_name,
            'value': force_text(self._value),
        }

    def __setstate__(self, state):
        from yepes.loading import get_model
        model = get_model(state['app'], state['model'])
        self._field = model._meta.get_field(state['field'])
        self._value = int(state['value'])

    def get_flags(self):
        return self._field.flags

