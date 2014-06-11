# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from django.utils import six
from django.utils.encoding import force_str, force_text
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext as _

from yepes.exceptions import MissingAttributeError, ReadOnlyObjectError


@python_2_unicode_compatible
class Bit(object):

    def __new__(cls, value=None, field=None):
        self = object.__new__(cls)
        self._field = field
        self._value = int(value or 0)
        return self

    def __getattr__(self, name):
        if not (self._field is None or name.startswith('_')):
            flag = getattr(self._field.flags, name)
            return bool(self._value & flag._value)
        else:
            raise MissingAttributeError(self, name)

    def __setattr__(self, name, value):
        if name.startswith('_'):
            object.__setattr__(self, name, value)
        elif self._field is not None:
            flag = getattr(self._field.flags, name)
            x = self._value
            y = flag._value
            z = (x | y) if value else ((x | y) ^ y)
            object.__setattr__(self, '_value', z)
        else:
            raise ReadOnlyObjectError(self)

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
            return _('(None)')
        else:
            verbose_names = self._field.flags.iter_verbose_names(self._value)
            return ', '.join(force_text(n) for n in verbose_names)

    def __bool__(self):
        return bool(self._value)

    def __int__(self):
        return self._value

    __nonzero__ = __bool__

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
        return self.__class__(self._value & other, self._field)

    __rand__ = __and__

    def __or__(self, other):
        if isinstance(other, Bit):
            assert other._field == self._field
            other = other._value
        return self.__class__(self._value | other, self._field)

    __ror__ = __or__

    def __xor__(self, other):
        if isinstance(other, Bit):
            assert other._field == self._field
            other = other._value
        return self.__class__(self._value ^ other, self._field)

    __rxor__ = __xor__

    def __invert__(self):
        if self._field:
            max_value = self._field.flags.get_max_value()
        else:
            max_value = (2 ** (len(bin(self._value)) - 2)) - 1
        return self.__class__(self._value ^ max_value, self._field)

    def __getstate__(self):
        return {
            'app': self._field.model._meta.app_label,
            'model': self._field.model._meta.object_name,
            'field': self._field.name,
            'value': force_text(self._value),
        }

    def __setstate__(self, state):
        from yepes.loading import get_model
        model = get_model(state['app'], state['model'])
        self._field = model._meta.get_field(state['field'])
        self._value = int(state['value'])

    def get_flags(self):
        return self._field.flags

