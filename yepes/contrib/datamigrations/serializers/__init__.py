# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from yepes.conf import settings
from yepes.contrib.datamigrations.serializers.base import Serializer
from yepes.utils.modules import import_module

__all__ = (
    'MissingSerializerError',
    'serialize', 'deserialize',
    'get_serializer', 'has_serializer', 'register_serializer',
    'Serializer',
    'serializers',
)

BUILTIN_SERIALIZERS = {
    'csv': 'yepes.contrib.datamigrations.serializers.csv.CsvSerializer',
    'json': 'yepes.contrib.datamigrations.serializers.json.JsonSerializer',
    'tsv': 'yepes.contrib.datamigrations.serializers.tsv.TsvSerializer',
    'yaml': 'yepes.contrib.datamigrations.serializers.yaml.YamlSerializer',
}

MissingSerializerError = LookupError


class SerializerHandler(object):
    """
    A Serializer Handler to retrieve Serializer classes.
    """
    def __init__(self):
        self._classes = {}
        self._registry =  {}
        self._registry.update(BUILTIN_SERIALIZERS)
        self._registry.update(getattr(settings, 'DATA_SERIALIZERS', []))

    def __contains__(self, name):
        return self.has_serializer(name)

    def get_serializer(self, name):
        try:
            return self._classes[name]
        except KeyError:
            pass

        if name not in self._registry:
            msg = "Serializer '{0}' could not be found."
            raise LookupError(msg.format(name))

        serializer = self.import_serializer(self._registry[name])
        self._classes[name] = serializer
        return serializer

    def get_serializers(self):
        return (self.__getitem__(name) for name in self._registry)

    def has_serializer(self, name):
        return name in self._registry

    def import_serializer(self, path):
        module_path, class_name = path.rsplit('.', 1)
        module = import_module(module_path, ignore_internal_errors=True)
        return getattr(module, class_name, None)

    def register_serializer(self, name, path):
        self._registry[name] = path

serializers = SerializerHandler()


def serialize(format, headers, data, file=None, **parameters):
    s = serializers.get_serializer(format)(**parameters)
    return s.serialize(headers, data, file)


def deserialize(format, headers, source, **parameters):
    s = serializers.get_serializer(format)(**parameters)
    return s.deserialize(headers, source)


get_serializer = serializers.get_serializer
has_serializer = serializers.has_serializer
register_serializer = serializers.register_serializer

