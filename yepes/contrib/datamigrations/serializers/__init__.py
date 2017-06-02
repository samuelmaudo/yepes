# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from django.utils import six

from yepes.conf import settings
from yepes.contrib.datamigrations.serializers.base import Serializer
from yepes.utils.modules import import_module

__all__ = (
    'serializers',
    'serialize', 'deserialize',
    'get_serializer', 'has_serializer', 'register_serializer',
    'Serializer',
)

BUILTIN_SERIALIZERS = [
    'yepes.contrib.datamigrations.serializers.csv.CsvSerializer',
    'yepes.contrib.datamigrations.serializers.json.JsonSerializer',
    'yepes.contrib.datamigrations.serializers.tsv.TsvSerializer',
    'yepes.contrib.datamigrations.serializers.xls.XlsSerializer',
    'yepes.contrib.datamigrations.serializers.xlsx.XlsxSerializer',
    'yepes.contrib.datamigrations.serializers.yaml.YamlSerializer',
]


class SerializerRegistry(object):
    """
    A registry to retrieve Serializer classes.
    """
    def __init__(self):
        self._registry = {}

    def __contains__(self, name):
        return name in self._registry

    def get_serializer(self, name):
        if name not in self._registry:
            msg = "Serializer '{0}' could not be found."
            raise LookupError(msg.format(name))
        else:
            return self._registry[name]

    def get_serializers(self):
        return six.itervalues(self._registry)

    def has_serializer(self, name):
        return name in self._registry

    def import_serializer(self, path):
        module_path, class_name = path.rsplit('.', 1)
        module = import_module(module_path, ignore_internal_errors=True)
        return getattr(module, class_name, None)

    def register_serializer(self, serializer):
        if isinstance(serializer, six.string_types):
            serializer = self.import_serializer(serializer)

        if serializer is not None:
            self._registry[serializer.name] = serializer
            return True
        else:
            return False

serializers = SerializerRegistry()
for path in BUILTIN_SERIALIZERS:
    serializers.register_serializer(path)
for path in settings.DATA_SERIALIZERS:
    serializers.register_serializer(path)


def serialize(format, headers, data, file=None, **parameters):
    s = serializers.get_serializer(format)(**parameters)
    return s.serialize(headers, data, file)


def deserialize(format, headers, source, **parameters):
    s = serializers.get_serializer(format)(**parameters)
    return s.deserialize(headers, source)


get_serializer = serializers.get_serializer
has_serializer = serializers.has_serializer
register_serializer = serializers.register_serializer

