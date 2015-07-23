# -*- coding:utf-8 -*-

from __future__ import division, unicode_literals

import math

from django.core.exceptions import (
    ImproperlyConfigured,
    ObjectDoesNotExist,
    ValidationError,
)
from django.core.validators import MaxValueValidator, EMPTY_VALUES
from django.db import models
from django.db.models import signals
from django.db.models.fields.related import add_lazy_relation
from django.utils import six
from django.utils.encoding import smart_text
from django.utils.six.moves import range, zip
from django.utils.text import capfirst

from yepes import forms
from yepes.exceptions import LookupTypeError, MissingAttributeError
from yepes.types import Bit, Undefined

__all__ = ('BitField', 'BitFieldDescriptor',
           'BitFieldFlags', 'BitFieldQueryWrapper',
           'RelatedBitField', 'RelatedBitFieldFlags',
           'UnknownFlagError')


class UnknownFlagError(ValueError):

    def __init__(self, field, value):
        if isinstance(value, six.string_types):
            msg = "Binary field '{0}' has no flag named '{1}'."
        else:
            value = bin(value)
            msg = "Binary field '{0}' has no flag {1}."
        super(UnknownFlagError, self).__init__(msg.format(field.name, value))


class BitField(models.BigIntegerField):

    choices = []
    __choices = Undefined
    empty_strings_allowed = False

    def __init__(self, verbose_name=None, name=None, choices=None, **kwargs):
        if not choices:
            raise TypeError('You must specify one or more choices.')
        super(BitField, self).__init__(verbose_name, name, **kwargs)
        self.flags = BitFieldFlags(self, choices)
        self.int_fields = int(math.ceil(len(choices) / 63))
        self.validators = [MaxValueValidator(self.flags.get_max_value())]

    def contribute_to_class(self, cls, name):
        super(BitField, self).contribute_to_class(cls, name)
        if self.int_fields > 1:
            counter = self.creation_counter
            for i in range(2, self.int_fields + 1):
                fld = models.BigIntegerField(
                    editable=False,
                    default=0,
                    blank=True,
                    null=self.null,
                    db_column='{0}_{1}'.format(self.column, i),
                    verbose_name='{0} ({1})'.format(self.verbose_name, i),
                )
                counter -= 0.001
                fld.creation_counter = counter
                fld.contribute_to_class(cls, '{0}_{1}'.format(self.name, i))

        setattr(cls, self.name, BitFieldDescriptor(self))

    def deconstruct(self):
        name, path, args, kwargs = super(BitField, self).deconstruct()
        path = path.replace('yepes.fields.bit', 'yepes.fields')
        kwargs['choices'] = tuple(zip(
            self.flags.iter_names(),
            self.flags.iter_verbose_names(),
        ))
        return name, path, args, kwargs

    def formfield(self, **kwargs):
        params = {
            'choices': self.get_choices(include_blank=False),
            'form_class': forms.BitField,
            'help_text': self.help_text,
            'label': capfirst(self.verbose_name),
            'required': not self.blank,
        }
        if self.has_default():
            if callable(self.default):
                params['initial'] = self.default
                params['show_hidden_initial'] = True
            else:
                params['initial'] = self.flags.get_value(self.get_default())

        params.update(kwargs)
        form_class = params.pop('form_class')
        if not isinstance(form_class, forms.BitField):
            form_class = forms.BitField

        return form_class(**params)

    def get_db_prep_lookup(self, lookup_type, value, connection, prepared=False):
        if not prepared:
            value = self.get_prep_lookup(lookup_type, value)

        if lookup_type in ('exact', 'isnull'):
            return BitFieldQueryWrapper(self, value)
        else:
            raise LookupTypeError(lookup_type)

    def get_db_prep_save(self, value, connection):
        value = models.Field.get_db_prep_save(self, value, connection)
        return self.split_value(value)[0]

    def get_choices(self, *args, **kwargs):
        if self.__choices is Undefined:
            self.__choices = [
                (int(value), smart_text(name))
                for value, name
                in zip(self.flags.iter_values(),
                       self.flags.iter_verbose_names())
            ]
        return self.__choices

    def get_default(self):
        if self.has_default():
            return self.default
        else:
            return None

    def get_prep_lookup(self, lookup_type, value):
        # We only handle 'exact' and 'isnull'. All others are errors.
        if lookup_type == 'exact':
            return self.get_prep_value(value)
        elif lookup_type == 'isnull':
            return value
        else:
            raise LookupTypeError(lookup_type)

    def get_prep_value(self, value):
        value = models.Field.get_prep_value(self, value)
        return self.flags.get_value(value)

    def join_value(self, pieces):
        value = 0
        for i, pc in enumerate(pieces):
            value += pc << (i * 63)

        return value

    def split_value(self, value):
        value = bin(int(value))[2:]
        pieces = list()
        for i in range(0, len(value), 63):
            if i > 0:
                pieces.append(int(value[-(i+63):-i], 2))
            else:
                pieces.append(int(value[-63:], 2))

        return pieces

    def to_python(self, value):
        # Although the descriptor ensures valid values, is necessary to
        # overwrite this method because the parent method coerces to ``int``.
        return value

    def validate(self, value, model_instance):
        if value is None and not self.null:
            raise ValidationError(self.error_messages['null'])
        if not self.blank and value in EMPTY_VALUES:
            raise ValidationError(self.error_messages['blank'])

    def value_to_string(self, obj):
        return int(self._get_val_from_obj(obj))


class BitFieldDescriptor(object):

    def __init__(self, field):
        self.field = field
        self.flags = field.flags
        self.attrs = [
            '{0}_{1}'.format(field.name, i + 1)
            for i in range(field.int_fields)
        ]
        self.cache_attr = field.name
        self.first_attr = self.attrs[0]

    def __get__(self, obj, cls=None):
        if obj is not None:
            if self.cache_attr not in obj.__dict__:
                obj.__dict__[self.cache_attr] = Bit(
                    self.field.join_value(
                        obj.__dict__[attr]
                        for attr
                        in self.attrs
                    ),
                    self.field,
                )
            return obj.__dict__[self.cache_attr]
        elif cls is not None:
            return self.flags
        else:
            return self

    def __set__(self, obj, value):
        if obj is None:
            msg = '`{0}` must be accessed via instance.'
            raise AttributeError(msg.format(self.field.name))

        if isinstance(value, six.integer_types):
            if self.first_attr not in obj.__dict__:
                # This is intended for quickly load values from database.
                obj.__dict__[self.first_attr] = value
            else:
                raise TypeError('Bit fields do not accept integer values.')
        else:
            value = self.flags.get_value(value)
            pieces = self.field.split_value(value)
            for i, attr in enumerate(self.attrs):
                if i < len(pieces):
                    obj.__dict__[attr] = pieces[i]
                else:
                    obj.__dict__[attr] = 0

            obj.__dict__[self.cache_attr] = Bit(value, self.field)


class BitFieldFlags(object):

    def __init__(self, field, choices):
        self._names = []
        self._verbose_names = []
        self._bits = []
        for i, choice in enumerate(choices):
            name, verbose = choice
            bit = Bit(2 ** i, field)
            self._names.append(name)
            self._verbose_names.append(verbose)
            self._bits.append(bit)
        self._field = field
        self._max_value = (2 ** (i + 1)) - 1

    def __getattr__(self, name):
        if name.startswith('_'):
            raise MissingAttributeError(self, name)
        try:
            return self.get_value(name)
        except UnknownFlagError as e:
            raise AttributeError(six.text_type(e))

    def get_name(self, value):
        for i, bit in enumerate(self._bits):
            if value == bit:
                return self._names[i]
        else:
            raise UnknownFlagError(self._field, value)

    def iter_names(self, filter=None):
        if filter is not None:
            names = (
                self._names[i]
                for i, bit
                in enumerate(self._bits)
                if filter & bit
            )
            return names
        else:
            return iter(self._names)

    def get_value(self, name):
        if isinstance(name, (tuple, list)):
            value = 0
            for n in name:
                value |= self._get_value(n)
            return value
        else:
            return self._get_value(name)

    def _get_value(self, name):
        if not name:
            return 0
        elif isinstance(name, (Bit, six.integer_types)):
            return name
        elif isinstance(name, six.string_types):
            for i, n in enumerate(self._names):
                if name == n:
                    return self._bits[i]
            else:
                raise UnknownFlagError(self._field, name)
        else:
            msg = 'String was expected, {0!r} received.'
            raise TypeError(msg.format(name))

    def iter_values(self):
        return iter(self._bits)

    def get_verbose_name(self, value):
        if isinstance(value, six.string_types):
            for i, name in enumerate(self._names):
                if value == name:
                    return self._verbose_names[i]
            else:
                raise UnknownFlagError(self._field, value)
        else:
            for i, bit in enumerate(self._bits):
                if value == bit:
                    return self._verbose_names[i]
            else:
                raise UnknownFlagError(self._field, value)

    def iter_verbose_names(self, filter=None):
        if filter is not None:
            names = (
                self._verbose_names[i]
                for i, bit
                in enumerate(self._bits)
                if filter & bit
            )
            return names
        else:
            return iter(self._verbose_names)

    def get_max_value(self):
        return self._max_value


class BitFieldQueryWrapper(object):

    def __init__(self, field, value):
        self.field = field
        self.value = value

    def as_sql(self, qn, connection=None):
        t = qn(self.field.model._meta.db_table)
        col = qn(self.field.column)

        if self.field.int_fields == 1:
            if not self.value:
                sql = '0'
            else:
                sql = '({0}.{1} | {2})'.format(t, col, int(self.value))
        else:
            if not self.value:
                conditions = ['0']
                cond = '{0}.{1} = 0'
                for i in range(self.field.int_fields - 1):
                    col = qn('{0}_{1}'.format(self.field.column, i + 2))
                    conditions.append(cond.format(t, col))
                sql = ' AND '.join(conditions)
            else:
                values = self.field.split_value(self.value)

                cond = '({0}.{1} | {2})'
                val = values[0]
                conditions = [cond.format(t, col, val)]

                cond = '{0}.{1} = ({0}.{1} | {2})'
                for i, val in enumerate(values[1:]):
                    col = qn('{0}_{1}'.format(self.field.column, i + 2))
                    conditions.append(cond.format(t, col, val))

                sql = ' AND '.join(conditions)

        return (sql, [])


class FakeRel(object):

    def __init__(self, to, field_name, limit_choices_to=None):
        self.to = to
        self.field_name = field_name
        self.limit_choices_to = limit_choices_to


class RelatedBitField(BitField):

    def __init__(self, to, to_field=None, allowed_choices=63,
                       limit_choices_to=None, **kwargs):
        super(BitField, self).__init__(**kwargs)
        self.fake_rel = FakeRel(to, to_field, limit_choices_to)
        self.flags = RelatedBitFieldFlags(self)
        self.int_fields = int(math.ceil(allowed_choices / 63))

    def contribute_to_class(self, cls, name):
        super(RelatedBitField, self).contribute_to_class(cls, name)
        other = self.fake_rel.to
        if isinstance(other, six.string_types) or other._meta.pk is None:
            def resolve_related_class(field, model, cls):
                rel = field.fake_rel
                rel.to = model
                rel.field_name = rel.field_name or model._meta.pk.name
            add_lazy_relation(cls, self, other, resolve_related_class)
        else:
            rel = self.fake_rel
            rel.field_name = rel.field_name or other._meta.pk.name

    def deconstruct(self):
        name, path, args, kwargs = super(BitField, self).deconstruct()
        path = path.replace('yepes.fields.bit', 'yepes.fields')
        kwargs['to'] = self.fake_rel.to
        kwargs['to_field'] = self.fake_rel.field_name
        kwargs['allowed_choices'] = self.int_fields * 63
        kwargs['limit_choices_to'] = self.fake_rel.limit_choices_to
        return name, path, args, kwargs

    def get_choices(self, *args, **kwargs):
        # Returns an instance of RelatedBitFieldChoices, a generator that uses
        # field flags to generate choices. It resets field flags before begin
        # choices generation.
        return RelatedBitFieldChoices(self)


class RelatedBitFieldFlags(object):

    _instances = Undefined
    _max_value = Undefined
    _queryset = Undefined
    _values = Undefined
    _verbose_names = Undefined

    def __init__(self, field):
        self._field = field

    def get_instance(self, value):
        if isinstance(value, six.string_types):
            raise NotImplementedError
        try:
            return self.get_queryset().get(pk=len(bin(value)) - 2)
        except ObjectDoesNotExist:
            raise UnknownFlagError(self._field, value)

    def get_queryset(self):
        if self._queryset is Undefined:
            rel = self._field.fake_rel
            if isinstance(rel.to, six.string_types):
                msg = "Model with name '{0}' could not be found."
                raise ImproperlyConfigured(msg.format(rel.to))
            qs = rel.to._default_manager.get_queryset()
            if rel.limit_choices_to:
                qs = qs.filter(**rel.limit_choices_to)
            self._queryset = qs
        return self._queryset.all()

    def iter_instances(self, filter=None):
        if filter:
            values = [
                i + 1
                for i, bit
                in enumerate(reversed(bin(int(filter))[2:]))
                if bit == '1'
            ]
            return self.get_queryset().filter(pk__in=values)
        else:
            if self._instances is Undefined:
                self._instances = self.get_queryset()
            return self._instances

    def get_name(self, value):
        raise NotImplementedError

    def iter_names(self, filter=None):
        raise NotImplementedError

    def get_value(self, instance):
        if isinstance(instance, (tuple, list)):
            value = 0
            for i in instance:
                value |= self._get_value(i)
            return value
        else:
            return self._get_value(instance)

    def _get_value(self, instance):
        if not instance:
            return 0
        elif isinstance(instance, (Bit, six.integer_types)):
            return instance
        elif isinstance(instance, self._field.fake_rel.to):
            return 2 ** (instance.pk - 1)
        else:
            cls_name = self._field.fake_rel.to.__name__
            msg = '{0} instance was expected, {1!r} received.'
            raise TypeError(msg.format(cls_name, instance))

    def iter_values(self):
        if self._values is Undefined:
            self._values = [
                2 ** (pk - 1)
                for pk
                in self.get_queryset().values_list('pk', flat=True)
            ]
        return self._values

    def get_verbose_name(self, value):
        return smart_text(self.get_instance(value))

    def iter_verbose_names(self, filter=None):
        if filter:
            return (
                smart_text(instance)
                for instance
                in self.iter_instances(filter)
            )
        else:
            if self._verbose_names is Undefined:
                self._verbose_names = (
                    smart_text(instance)
                    for instance
                    in self.iter_instances()
                )
            return self._verbose_names

    def get_max_value(self):
        if self._max_value is Undefined:
            pk = self.get_queryset().aggregate(models.Max('pk'))['pk__max']
            if not pk:
                self._max_value = 0
            else:
                self._max_value = (2 ** pk) - 1

        return self._max_value

    def reset(self, *args, **kwargs):
        self._instances = Undefined
        self._max_value = Undefined
        self._values = Undefined
        self._verbose_names = Undefined


class RelatedBitFieldChoices(object):

    def __init__(self, field):
        self._field = field

    def __iter__(self):
        flags = self._field.flags
        flags.reset()
        choices = zip(flags.iter_values(), flags.iter_verbose_names())
        for value, name in choices:
            yield (int(value), smart_text(name))

