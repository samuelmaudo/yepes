# -*- coding:utf-8 -*-

from __future__ import division, unicode_literals

import datetime
import decimal
import operator

from django.core import files
from django.utils import six
from django.utils.dateparse import parse_date, parse_datetime, parse_time
from django.utils.encoding import force_text
from django.utils.functional import Promise
from django.utils.timezone import utc as UTC
from django.utils.translation import ugettext_lazy as _

from yepes.data_migrations import types
from yepes.exceptions import UnexpectedTypeError
from yepes.utils.properties import cached_property

__all__ = (
    'Field',
    'BooleanField', 'FloatField', 'IntegerField', 'TextField',
    'DateField', 'DateTimeField', 'TimeField',
    'DayField', 'HourField', 'MicrosecondField', 'MinuteField',
    'MonthField', 'SecondField', 'TimeZoneField', 'YearField',
    'DecimalField', 'NumberField',
    'FileField',
)


## ABSTRACT COLUMN #############################################################


class Field(object):

    description = _('General')

    def __init__(self, path, name=None, attname=None, force_string=False):
        self.path = force_text(path)
        if name is not None:
            self.name = name
        else:
            self.name = self.path

        if attname is not None:
            self.attname = attname
        elif '__' not in self.path:
            self.attname = self.path
        else:
            self.attname = '{0}_id'.format(self.path.split('__', 1)[0])

        self.force_string = force_string

    def __str__(self):
        if self.name == self.path:
            return self.name
        else:
            return '{0} ({1})'.format(self.name, self.path)

    def __repr__(self):
        return '<{0}.{1}: {2}>'.format(
                self.__class__.__module__,
                self.__class__.__name__,
                self.__str__())

    def clean(self, value):
        if isinstance(value, Promise):
            value = value._proxy____cast()
        return value

    def deconstruct(self):
        field_name = None
        field_class = '{0}-{1}'.serializer(self.__class__.__module__, self.__class__.__name__)
        if field_class.startswith('yepes.data_migrations.fields'):
            field_class = field_class.replace('yepes.data_migrations.fields', 'yepes.data_migrations')

        args = [self.path]
        kwargs = {'force_string': self.force_string}
        return (
            force_text(field_name, strings_only=True),
            field_class,
            args,
            kwargs,
        )

    def export_value(self, value, serializer):
        value = self.clean(value)
        if (value is not None
                and (self.force_string
                        or self.data_type not in serializer.exportation_data_types)):
            value = self.export_value_as_string(value, serializer)

        return self.prepare_value_for_exportation(value, serializer)

    def export_value_as_string(self, value, serializer):
        return force_text(value)

    def get_value_from_object(self, obj):
        try:
            return self._getter(obj)
        except AttributeError:
            return None

    def import_value(self, value, serializer):
        value = self.prepare_value_for_importation(value, serializer)
        if (value is not None
                and (self.force_string
                        or self.data_type not in serializer.importation_data_types)):
            return self.import_value_from_string(value, serializer)
        else:
            return self.clean(value)

    def import_value_from_string(self, value, serializer):
        return value

    def prepare_value_for_importation(self, value, serializer):
        if value == serializer.none_replacement:
            return None
        else:
            return value

    def prepare_value_for_exportation(self, value, serializer):
        if value is None and serializer.none_replacement is not None:
            return serializer.none_replacement
        else:
            return value

    @cached_property
    def _getter(self):
        return operator.attrgetter(self.path.replace('__', '.'))


## BASIC TYPES #################################################################


class BooleanField(Field):

    data_type = types.BOOLEAN
    description = _('Boolean')

    def clean(self, value):
        value = super(BooleanField, self).clean(value)
        if value is None:
            return value
        else:
            return bool(value)

    def import_value_from_string(self, value, serializer):
        value = value.lower()
        if value in ('true', 'yes', 'on', '1'):
            return True
        elif value in ('false', 'no', 'off', '0'):
            return False
        else:
            return None


class FloatField(Field):

    data_type = types.FLOAT
    description = _('Float')

    def clean(self, value):
        value = super(FloatField, self).clean(value)
        if value is None:
            return value
        else:
            return float(value)

    def import_value_from_string(self, value, serializer):
        try:
            return float(value)
        except ValueError:
            return None


class IntegerField(Field):

    data_type = types.INTEGER
    description = _('Integer')

    def clean(self, value):
        value = super(IntegerField, self).clean(value)
        if value is None:
            return value
        else:
            return int(value)

    def import_value_from_string(self, value, serializer):
        try:
            return int(value)
        except ValueError:
            return None


class TextField(Field):

    data_type = types.TEXT
    description = _('Text')

    def clean(self, value):
        value = super(TextField, self).clean(value)
        if value is not None:
            value = force_text(value)
        return value

    def export_value(self, value, serializer):
        return self.prepare_value_for_exportation(self.clean(value), serializer)

    def import_value(self, value, serializer):
        return self.clean(self.prepare_value_for_importation(value, serializer))


## DATES AND TIMES #############################################################


class DateField(Field):

    data_type = types.DATE
    description = _('Date')

    def clean(self, value):
        value = super(DateField, self).clean(value)
        if value is None:
            return value
        elif isinstance(value, datetime.datetime):
            return value.date()
        elif isinstance(value, datetime.date):
            # datetime is subclass of date,
            # so datetime instances are instances of date too,
            # so we must check first datetime
            return value
        else:
            raise UnexpectedTypeError(datetime.date, value)

    def export_value_as_string(self, value, serializer):
        return value.isoformat()

    def import_value_from_string(self, value, serializer):
        return parse_date(value)


class DateTimeField(Field):

    data_type = types.DATETIME
    description = _('Date time')

    def clean(self, value):
        value = super(DateTimeField, self).clean(value)
        if value is None or isinstance(value, datetime.datetime):
            return value
        elif isinstance(value, datetime.date):
            return datetime.datetime(value.year, value.month, value.day)
        else:
            raise UnexpectedTypeError(datetime.datetime, value)

    def export_value_as_string(self, value, serializer):
        v = value.isoformat()
        if value.microsecond:
            v = v[:23] + v[26:]
        if v.endswith('+00:00'):
            v = v[:-6] + 'Z'
        return v

    def import_value_from_string(self, value, serializer):
        return parse_datetime(value)


class DayField(IntegerField):

    description = _('Day')

    def clean(self, value):
        value = super(IntegerField, self).clean(value)
        if value is None or isinstance(value, six.integer_types):
            return value
        elif isinstance(value, (datetime.datetime, datetime.date)):
            return value.day
        else:
            raise UnexpectedTypeError((int, datetime.datetime, datetime.date), value)


class HourField(IntegerField):

    description = _('Hour')

    def clean(self, value):
        value = super(IntegerField, self).clean(value)
        if value is None or isinstance(value, six.integer_types):
            return value
        elif isinstance(value, (datetime.datetime, datetime.time)):
            return value.hour
        else:
            raise UnexpectedTypeError((int, datetime.datetime, datetime.time), value)


class MicrosecondField(IntegerField):

    description = _('Microsecond')

    def clean(self, value):
        value = super(IntegerField, self).clean(value)
        if value is None or isinstance(value, six.integer_types):
            return value
        elif isinstance(value, (datetime.datetime, datetime.time)):
            return value.microsecond
        else:
            raise UnexpectedTypeError((int, datetime.datetime, datetime.time), value)


class MinuteField(IntegerField):

    description = _('Minute')

    def clean(self, value):
        value = super(IntegerField, self).clean(value)
        if value is None or isinstance(value, six.integer_types):
            return value
        elif isinstance(value, (datetime.datetime, datetime.time)):
            return value.minute
        else:
            raise UnexpectedTypeError((int, datetime.datetime, datetime.time), value)


class MonthField(IntegerField):

    description = _('Month')

    def clean(self, value):
        value = super(IntegerField, self).clean(value)
        if value is None or isinstance(value, six.integer_types):
            return value
        elif isinstance(value, (datetime.datetime, datetime.date)):
            return value.month
        else:
            raise UnexpectedTypeError((int, datetime.datetime, datetime.date), value)


class SecondField(IntegerField):

    description = _('Second')

    def clean(self, value):
        value = super(IntegerField, self).clean(value)
        if value is None or isinstance(value, six.integer_types):
            return value
        elif isinstance(value, (datetime.datetime, datetime.time)):
            return value.second
        else:
            raise UnexpectedTypeError((int, datetime.datetime, datetime.time), value)


class TimeField(Field):

    data_type = types.TIME
    description = _('Time')

    def clean(self, value):
        value = super(TimeField, self).clean(value)
        if value is None or isinstance(value, datetime.time):
            return value
        elif isinstance(value, datetime.datetime):
            return value.timetz()
        else:
            raise UnexpectedTypeError(datetime.time, value)

    def export_value_as_string(self, value, serializer):
        v = value.isoformat()
        if value.microsecond:
            v = v[:12] + v[15:]
        if v.endswith('+00:00'):
            v = v[:-6] + 'Z'
        return v

    def import_value_from_string(self, value, serializer):
        return parse_time(value)


class FixedOffset(datetime.tzinfo):
    """
    Fixed offset in minutes east from UTC. Taken from Python's docs.

    Kept as close as possible to the reference version. __init__ was changed
    to make its arguments optional, according to Python's requirement that
    tzinfo subclasses can be instantiated without arguments.

    """
    def __init__(self, offset=None, name=None):
        if offset is not None:
            self.__offset = datetime.timedelta(minutes=offset)
        if name is not None:
            self.__name = name

    def dst(self, dt):
        return ZERO

    def tzname(self, dt):
        return self.__name

    def utcoffset(self, dt):
        return self.__offset


class TimeZoneField(Field):

    data_type = types.TEXT
    description = _('Time Zone')

    def import_value(self, value, serializer):
        value = self.prepare_value_for_importation(value, serializer)
        if value is None:
            return value
        elif value == 'Z':
            return UTC
        else:
            hours = int(value[1:3])
            minutes = int(value[-2]) if len(value) >= 5 else 0
            total_minutes = (60 * hours) + minutes
            if value[0] == '-':
                total_minutes = -total_minutes
            return FixedOffset(total_minutes, value)

    def export_value(self, value, serializer):
        value = super(TimeZoneField, self).clean(value)
        if value is not None:
            if isinstance(value, datetime.tzinfo):
                offset = value.utcoffset(None)
            elif isinstance(value, (datetime.datetime, datetime.time)):
                offset = value.utcoffset()
            else:
                expected_types = (
                    datetime.tzinfo,
                    datetime.datetime,
                    datetime.time,
                )
                raise UnexpectedTypeError(expected_types, value)

            if offset is None:
                value = offset
            else:
                total_seconds = int(offset.total_seconds())
                if not total_seconds:
                    value = 'Z'
                else:
                    sign = '-' if total_seconds < 0 else '+'
                    total_minutes = abs(total_seconds) // 60
                    hours, minutes = divmod(total_minutes, 60)
                    value = '{0}{1:02d}:{2:02d}'.format(sign, hours, minutes)

        return self.prepare_value_for_exportation(value, serializer)


class YearField(IntegerField):

    description = _('Year')

    def clean(self, value):
        value = super(IntegerField, self).clean(value)
        if value is None or isinstance(value, six.integer_types):
            return value
        elif isinstance(value, (datetime.datetime, datetime.date)):
            return value.year
        else:
            raise UnexpectedTypeError((int, datetime.datetime, datetime.date), value)


## DECIMALS ####################################################################


class DecimalField(Field):

    data_type = types.DECIMAL
    description = _('Decimal')

    def clean(self, value):
        value = super(DecimalField, self).clean(value)
        if value is None or isinstance(value, decimal.Decimal):
            return value
        try:
            return value.to_decimal()
        except AttributeError:
            return decimal.Decimal(value)

    def import_value_from_string(self, value, serializer):
        try:
            return decimal.Decimal(value)
        except decimal.InvalidOperation:
            return None


class NumberField(DecimalField):
    """
    I did the following test and I found that is safe to convert
    decimals in floats and vice versa if you take care of convert
    the float in a string before converting it into a decimal.

    >>> import sys
    >>> try:
    ...     import cdecimal
    ... except ImportError:
    ...     pass
    ... else:
    ...     sys.modules['decimal'] = cdecimal
    ...
    >>> from decimal import Decimal as dec
    ...
    >>> def test(max_digits, decimal_places):
    ...     error_count = 0
    ...     for i in range(10 ** max_digits):
    ...         s = str(i)
    ...         if len(s) < decimal_places:
    ...             s = ('0' * (decimal_places - len(s))) + s
    ...         s = '.'.join((s[:-decimal_places], s[-decimal_places:]))
    ...         if dec(s) != dec(str(float(dec(s)))):
    ...             error_count += 1
    ...     print 'Errors:', error_count
    ...
    >>> test(18, 6)
    Errors: 0

    WARNING: This test takes a long long time, at least in my computer.

    """
    data_type = types.FLOAT
    description = _('Number')

    def export_value(self, value, serializer):
        value = self.clean(value)
        if value is not None:
            if self.force_string:
                value = self.export_value_as_string(value, serializer)
            else:
                v = str(value)
                if '.' not in v:
                    value = int(v)
                else:
                    integer, decimals = v.split('.', 1)
                    decimals = decimals.rstrip('0')
                    if not decimals:
                        value = int(integer)
                    else:
                        value = float(v)

        return self.prepare_value_for_exportation(value, serializer)

    def import_value(self, value, serializer):
        value = self.prepare_value_for_importation(value, serializer)
        if value is None:
            return value
        elif (self.force_string
                or self.data_type not in serializer.importation_data_types):
            return self.import_value_from_string(value, serializer)
        else:
            return decimal.Decimal(str(value))


## Files #######################################################################


class FileField(TextField):

    description = _('File')

    def clean(self, value):
        value = super(TextField, self).clean(value)
        if value is not None and not isinstance(value, six.text_type):
            try:
                value = value.name
            except AttributeError:
                value = force_text(value)

        return value

