# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from django.utils import six
from django.utils.six.moves import cStringIO

from yepes.contrib.data_migrations.types import BOOLEAN, FLOAT, INTEGER, TEXT


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

    def __init__(self, **serializer_parameters):
        self.none_replacement = serializer_parameters.pop('nonereplacement', None)
        self.serializer_parameters = serializer_parameters

    def deserialize(self, headers, source):
        if isinstance(source, six.string_types):
            return self.loads(headers, source)
        else:
            return self.load(headers, source)

    def dump(self, headers, data, file):
        raise NotImplementedError('Subclasses of Serializer must override dump() method')

    def dumps(self, headers, data):
        stream = cStringIO()
        self.dump(headers, data, stream)
        return stream.getvalue()

    def load(self, headers, file):
        raise NotImplementedError('Subclasses of Serializer must override load() method')

    def loads(self, headers, string):
        return self.load(headers, cStringIO(string))

    def serialize(self, headers, data, file=None):
        if file is None:
            return self.dumps(headers, data)
        else:
            self.dump(headers, data, file)
            return None

