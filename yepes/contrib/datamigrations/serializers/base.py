# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from io import open, BytesIO, StringIO

from django.utils import six
from django.utils.text import camel_case_to_spaces, capfirst

from yepes.contrib.datamigrations.constants import BOOLEAN, FLOAT, INTEGER, TEXT
from yepes.utils.properties import class_property


class Serializer(object):
    """
    Base class for data-migration serializer implementations.

    Subclasses must at least overwrite ``dump()`` and ``load()``.

    """
    exportation_data_types = frozenset([
        TEXT,
        INTEGER,
        FLOAT,
        BOOLEAN,
    ])
    importation_data_types = frozenset([
        TEXT,
        INTEGER,
        FLOAT,
        BOOLEAN,
    ])
    is_binary = False

    @class_property
    def name(cls):
        name = camel_case_to_spaces(cls.__name__)
        if name.endswith('serializer'):
            name = name[:-11]
        return '_'.join(name.split())

    @class_property
    def verbose_name(cls):
        return capfirst(cls.name.replace('_', ' ').strip())

    def __init__(self, **serializer_parameters):
        self.encoding = serializer_parameters.pop('encoding', None)
        self.errors = serializer_parameters.pop('errors', None)
        self.newline = serializer_parameters.pop('newline', None)
        self.none_replacement = serializer_parameters.pop('nonereplacement', None)
        self.serializer_parameters = serializer_parameters

    def check_file(self, file):
        if self.is_binary:
            if 'b' not in getattr(file, 'mode', 'b'):
                raise TypeError('file must be bytes, not unicode')
        else:
            if 'b' in getattr(file, 'mode', ''):
                raise TypeError('file must be unicode, not bytes')

    def check_string(self, string):
        if self.is_binary:
            if isinstance(string, six.text_type):
                raise TypeError('string must be bytes, not unicode')
        else:
            if isinstance(string, six.binary_type):
                raise TypeError('string must be unicode, not bytes')

    def deserialize(self, headers, source):
        if isinstance(source, (six.binary_type, six.text_type)):
            self.check_string(source)
            return self.loads(headers, source)
        else:
            self.check_file(source)
            return self.load(headers, source)

    def dump(self, headers, data, file):
        raise NotImplementedError('Subclasses of Serializer must override dump() method')

    def dumps(self, headers, data):
        stream = BytesIO() if self.is_binary else StringIO()
        self.dump(headers, data, stream)
        return stream.getvalue()

    def load(self, headers, file):
        raise NotImplementedError('Subclasses of Serializer must override load() method')

    def loads(self, headers, string):
        stream_class = BytesIO if self.is_binary else StringIO
        return self.load(headers, stream_class(string))

    def open_to_dump(self, path):
        if self.is_binary:
            return open(path, 'wb')
        else:
            return open(path, 'wt', encoding=self.encoding, errors=self.errors, newline=self.newline)

    def open_to_load(self, path):
        if self.is_binary:
            return open(path, 'rb')
        else:
            return open(path, 'rt', encoding=self.encoding, errors=self.errors, newline=self.newline)

    def serialize(self, headers, data, file=None):
        if file is None:
            return self.dumps(headers, data)
        else:
            self.check_file(file)
            self.dump(headers, data, file)
            return None

