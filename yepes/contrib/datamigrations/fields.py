# -*- coding:utf-8 -*-

from __future__ import division, unicode_literals

from datetime import date, datetime, time, timedelta, tzinfo
from decimal import Decimal as dec, InvalidOperation
from operator import attrgetter

from django.core import files
from django.utils import six
from django.utils.dateparse import parse_date, parse_datetime, parse_time
from django.utils.encoding import force_str, force_text, python_2_unicode_compatible
from django.utils.functional import Promise
from django.utils.text import camel_case_to_spaces, capfirst
from django.utils.timezone import FixedOffset, utc as UTC
from django.utils.translation import ugettext_lazy as _

from yepes.contrib.datamigrations.constants import (
    BOOLEAN, FLOAT, INTEGER, TEXT,
    DATE, DATETIME, TIME,
    DECIMAL,
)
from yepes.exceptions import UnexpectedTypeError
from yepes.utils.properties import cached_property, class_property

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


@python_2_unicode_compatible
class Field(object):

    @class_property
    def description(cls):
        name = capfirst(camel_case_to_spaces(cls.__name__))
        if name.endswith('field'):
            name = name[:-6]
        return name

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
        args = (
            self.__class__.__module__,
            self.__class__.__name__,
            six.text_type(self),
        )
        return force_str('<{0}.{1}: {2}>'.format(*args))

    def clean(self, value):
        if isinstance(value, Promise):
            value = value._proxy____cast()
        return value

    def export_value(self, value, serializer):
        value = self.clean(value)
        if (value is not None
                and (self.force_string
                        or self.data_type not in serializer.exportation_data_types)):
            value = self.export_value_as_string(value, serializer)

        return self.prepare_to_export(value, serializer)

    def export_value_as_string(self, value, serializer):
        return force_text(value)

    def import_value(self, value, serializer):
        value = self.prepare_to_import(value, serializer)
        if (value is not None
                and (self.force_string
                        or self.data_type not in serializer.importation_data_types)):
            return self.import_value_from_string(value, serializer)
        else:
            return self.clean(value)

    def import_value_from_string(self, value, serializer):
        return value

    def prepare_to_export(self, value, serializer):
        if value is None:
            return serializer.none_replacement
        else:
            return value

    def prepare_to_import(self, value, serializer):
        if value == serializer.none_replacement:
            return None
        else:
            return value

    def value_from_object(self, obj):
        try:
            return self._getter(obj)
        except AttributeError:
            return None

    @cached_property
    def _getter(self):
        return attrgetter(self.path.replace('__', '.'))


## BASIC TYPES #################################################################


class BooleanField(Field):

    data_type = BOOLEAN
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

    data_type = FLOAT
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

    data_type = INTEGER
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

    data_type = TEXT
    description = _('Text')

    def clean(self, value):
        value = super(TextField, self).clean(value)
        if value is not None:
            value = force_text(value)
        return value

    def export_value(self, value, serializer):
        return self.prepare_to_export(self.clean(value), serializer)

    def import_value(self, value, serializer):
        return self.clean(self.prepare_to_import(value, serializer))


## DATES AND TIMES #############################################################


class DateField(Field):

    data_type = DATE
    description = _('Date')

    def clean(self, value):
        value = super(DateField, self).clean(value)
        if value is None:
            return value
        elif isinstance(value, datetime):
            return value.date()
        elif isinstance(value, date):
            # datetime is subclass of date,
            # so datetime instances are instances of date too,
            # so we must check first datetime
            return value
        else:
            raise UnexpectedTypeError(date, value)

    def export_value_as_string(self, value, serializer):
        return value.isoformat()

    def import_value_from_string(self, value, serializer):
        return parse_date(value)


class DateTimeField(Field):

    data_type = DATETIME
    description = _('Date Time')

    def clean(self, value):
        value = super(DateTimeField, self).clean(value)
        if value is None or isinstance(value, datetime):
            return value
        elif isinstance(value, date):
            return datetime(value.year, value.month, value.day)
        else:
            raise UnexpectedTypeError(datetime, value)

    def export_value_as_string(self, value, serializer):
        v = value.isoformat()
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
        elif isinstance(value, (datetime, date)):
            return value.day
        else:
            raise UnexpectedTypeError((int, datetime, date), value)


class HourField(IntegerField):

    description = _('Hour')

    def clean(self, value):
        value = super(IntegerField, self).clean(value)
        if value is None or isinstance(value, six.integer_types):
            return value
        elif isinstance(value, (datetime, time)):
            return value.hour
        else:
            raise UnexpectedTypeError((int, datetime, time), value)


class MicrosecondField(IntegerField):

    description = _('Microsecond')

    def clean(self, value):
        value = super(IntegerField, self).clean(value)
        if value is None or isinstance(value, six.integer_types):
            return value
        elif isinstance(value, (datetime, time)):
            return value.microsecond
        else:
            raise UnexpectedTypeError((int, datetime, time), value)


class MinuteField(IntegerField):

    description = _('Minute')

    def clean(self, value):
        value = super(IntegerField, self).clean(value)
        if value is None or isinstance(value, six.integer_types):
            return value
        elif isinstance(value, (datetime, time)):
            return value.minute
        else:
            raise UnexpectedTypeError((int, datetime, time), value)


class MonthField(IntegerField):

    description = _('Month')

    def clean(self, value):
        value = super(IntegerField, self).clean(value)
        if value is None or isinstance(value, six.integer_types):
            return value
        elif isinstance(value, (datetime, date)):
            return value.month
        else:
            raise UnexpectedTypeError((int, datetime, date), value)


class SecondField(IntegerField):

    description = _('Second')

    def clean(self, value):
        value = super(IntegerField, self).clean(value)
        if value is None or isinstance(value, six.integer_types):
            return value
        elif isinstance(value, (datetime, time)):
            return value.second
        else:
            raise UnexpectedTypeError((int, datetime, time), value)


class TimeField(Field):

    data_type = TIME
    description = _('Time')

    def clean(self, value):
        value = super(TimeField, self).clean(value)
        if value is None or isinstance(value, time):
            return value
        elif isinstance(value, datetime):
            return value.timetz()
        else:
            raise UnexpectedTypeError(time, value)

    def export_value_as_string(self, value, serializer):
        v = value.isoformat()
        if v.endswith('+00:00'):
            v = v[:-6] + 'Z'
        return v

    def import_value_from_string(self, value, serializer):
        return parse_time(value)


class TimeZoneField(Field):

    data_type = TEXT
    description = _('Time Zone')

    def import_value(self, value, serializer):
        value = self.prepare_to_import(value, serializer)
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
            if isinstance(value, tzinfo):
                offset = value.utcoffset(None)
            elif isinstance(value, (datetime, time)):
                offset = value.utcoffset()
            else:
                expected_types = (
                    tzinfo,
                    datetime,
                    time,
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

        return self.prepare_to_export(value, serializer)


class YearField(IntegerField):

    description = _('Year')

    def clean(self, value):
        value = super(IntegerField, self).clean(value)
        if value is None or isinstance(value, six.integer_types):
            return value
        elif isinstance(value, (datetime, date)):
            return value.year
        else:
            raise UnexpectedTypeError((int, datetime, date), value)


## DECIMALS ####################################################################


class DecimalField(Field):

    data_type = DECIMAL
    description = _('Decimal')

    def clean(self, value):
        value = super(DecimalField, self).clean(value)
        if value is None or isinstance(value, dec):
            return value
        try:
            return value.to_decimal()
        except AttributeError:
            return dec(value)

    def import_value_from_string(self, value, serializer):
        try:
            return dec(value)
        except InvalidOperation:
            return None


class NumberField(DecimalField):
    """
    I did the following test and I found that is safe to convert
    decimals in floats and vice versa if you take care of convert
    the float in a string before converting it into a

    >>> from decimal import Decimal as dec
    >>> def test(max_digits, decimal_places):
    ...     error_count = 0
    ...     for i in range(10 ** max_digits):
    ...         s = str(i).zfill(decimal_places)
    ...         s = s[:-decimal_places] + '.' + s[-decimal_places:]
    ...         d = dec(s)
    ...         if d != dec(str(float(d))):
    ...             print(s, str(float(d)), sep=' != ')
    ...             error_count += 1
    ...     print('ERRORS: ', error_count)
    ...
    >>> test(12, 6)
    ERRORS: 0

    WARNING: This test takes a long long time, at least in my computer.

    """
    data_type = FLOAT
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

        return self.prepare_to_export(value, serializer)

    def import_value(self, value, serializer):
        value = self.prepare_to_import(value, serializer)
        if value is None:
            return value
        elif (self.force_string
                or self.data_type not in serializer.importation_data_types):
            return self.import_value_from_string(value, serializer)
        else:
            return dec(str(value))


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

