# -*- coding:utf-8 -*-

from base64 import b64decode, b64encode
import zlib

from django.db import models
from django.utils import six
from django.utils.encoding import force_bytes, force_text

from yepes.exceptions import LookupTypeError
from yepes.utils.properties import cached_property


@six.add_metaclass(models.SubfieldBase)
class CompressedTextField(models.BinaryField):

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
        super(CompressedTextField, self).__init__(*args, **kwargs)
        self.editable = editable

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

    def get_prep_lookup(self, lookup_type, value):
        if lookup_type == 'exact':
            return self.get_prep_value(value)
        elif lookup_type == 'in':
            return [self.get_prep_value(v) for v in value]
        else:
            raise LookupTypeError(lookup_type)

    def get_prep_value(self, value):
        if value is not None:
            return self.compress(value)
        else:
            return value

    def south_field_triple(self):
        """
        Returns a suitable description of this field for South.
        """
        from south.modelsinspector import introspector
        field_class = 'django.db.models.fields.BinaryField'
        args, kwargs = introspector(self)
        return (field_class, args, kwargs)

    def to_python(self, value):
        if isinstance(value, six.binary_type):
            return self.decompress(value)
        elif isinstance(value, buffer if six.PY2 else memoryview):
            return self.decompress(six.binary_type(value))
        elif (isinstance(value, six.text_type)
                and value.startswith(self._prefix)
                and value.endswith(self._suffix)):
            return self.value_from_string()
        else:
            return value

    def value_from_string(self, string):
        compressed_value = string[self._prefix_len:-self._suffix_len]
        return self.decompress(b64decode(compressed_value.encode('ascii')))

    def value_to_string(self, obj):
        value = self._get_val_from_obj(obj)
        compressed_value = b64encode(self.compress(value)).decode('ascii')
        return ''.join(self._prefix, compressed_value, self._suffix)

