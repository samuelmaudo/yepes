# -*- coding:utf-8 -*-

from base64 import b64decode, b64encode
import zlib

from django import forms
from django.core.validators import MinLengthValidator
from django.db import models
from django.db.models.lookups import Exact, In
from django.utils import six
from django.utils.encoding import force_bytes, force_text
from django.utils.translation import ugettext_lazy as _

from yepes.fields.calculated import CalculatedField
from yepes.fields.char import (
    check_max_length_attribute,
    check_min_length_attribute
)
from yepes.utils.deconstruct import clean_keywords
from yepes.utils.properties import cached_property


class CompressedTextField(CalculatedField, models.BinaryField):

    description = _('Compressed text')

    _prefix = '({[#'
    _suffix = '#]})'

    @cached_property
    def _prefix_len(self):
        return len(self._prefix)

    @cached_property
    def _suffix_len(self):
        return len(self._suffix)

    def __init__(self, *args, **kwargs):
        self.compression_level = kwargs.pop('compression_level', 6)
        editable = kwargs.pop('editable', True)
        self.min_length = kwargs.pop('min_length', None)
        super(CompressedTextField, self).__init__(*args, **kwargs)
        self.editable = editable  # BinaryField sets editable == False
        if self.min_length is not None:
            self.validators.append(MinLengthValidator(self.min_length))

    def check(self, **kwargs):
        errors = super(CompressedTextField, self).check(**kwargs)
        errors.extend(self._check_max_length_attribute(**kwargs))
        errors.extend(self._check_min_length_attribute(**kwargs))
        return errors

    _check_max_length_attribute = check_max_length_attribute
    _check_min_length_attribute = check_min_length_attribute

    def compress(self, text):
        if not text:
            return b''
        bytes = force_text(text).encode('utf8')
        return zlib.compress(bytes, self.compression_level)

    def decompress(self, bytes):
        if not bytes:
            return ''
        bytes = zlib.decompress(force_bytes(bytes))
        return bytes.decode('utf8')

    def deconstruct(self):
        name, path, args, kwargs = super(models.BinaryField, self).deconstruct()
        path = path.replace('yepes.fields.compressed', 'yepes.fields')
        clean_keywords(self, kwargs, variables={
            'calculated': False,
            'compression_level': 6,
            'editable': True,
            'min_length': None,
        })
        return name, path, args, kwargs

    def formfield(self, **kwargs):
        kwargs.setdefault('form_class', forms.CharField)
        kwargs.setdefault('widget', forms.Textarea)
        kwargs.setdefault('min_length', self.min_length)
        kwargs.setdefault('max_length', self.max_length)
        return super(CompressedTextField, self).formfield(**kwargs)

    def from_db_value(self, value, expression, connection, context):
        if value is None:
            return value
        else:
            return self.decompress(value)

    def get_lookup(self, lookup_name):
        if lookup_name == 'exact':
            return Exact
        elif lookup_name == 'in':
            return In
        else:
            return None

    def get_prep_value(self, value):
        value = models.Field.get_prep_value(self, value)
        if value is None:
            return value
        else:
            return self.compress(value)

    def to_python(self, value):
        if isinstance(value, six.binary_type):
            return self.decompress(value)
        elif isinstance(value, buffer if six.PY2 else memoryview):
            return self.decompress(six.binary_type(value))
        elif (isinstance(value, six.text_type)
                and value.startswith(self._prefix)
                and value.endswith(self._suffix)):
            return self.value_from_string(value)
        else:
            return value

    def value_from_string(self, string):
        compressed_value = string[self._prefix_len:-self._suffix_len]
        return self.decompress(b64decode(compressed_value.encode('ascii')))

    def value_to_string(self, obj):
        value = self._get_val_from_obj(obj)
        compressed_value = b64encode(self.compress(value)).decode('ascii')
        return ''.join(self._prefix, compressed_value, self._suffix)

