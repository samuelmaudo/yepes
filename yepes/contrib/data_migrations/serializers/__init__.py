# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from django.utils import six

from yepes.conf import settings
from yepes.loading import get_module, LoadingError

BUILTIN_SERIALIZERS = {
    'csv': 'yepes.contrib.data_migrations.serializers.csv.CsvSerializer',
    'json': 'yepes.contrib.data_migrations.serializers.json.JsonSerializer',
    'tsv': 'yepes.contrib.data_migrations.serializers.tsv.TsvSerializer',
    'yaml': 'yepes.contrib.data_migrations.serializers.yaml.YamlSerializer',
}

_SERIALIZERS = None


class MissingSerializerError(LoadingError):

    def __init__(self, serializer_name):
        msg = "Serializer '{0}' could not be found."
        super(MissingSerializerError, self).__init__(msg.format(serializer_name))


def serialize(format, headers, data, file=None, **parameters):
    s = get_serializer(format)(**parameters)
    return s.serialize(headers, data, file)


def deserialize(format, headers, source, **parameters):
    s = get_serializer(format)(**parameters)
    return s.deserialize(headers, source)


def get_serializer(name):
    if not has_serializer(name):
        raise MissingSerializerError(name)
    else:
        return _SERIALIZERS[name]


def has_serializer(name):
    if _SERIALIZERS is None:
        _load_serializers()
    return (name in _SERIALIZERS)


def register_serializer(name, path):
    if _SERIALIZERS is None:
        _load_serializers()
    serializer_class = _import_serializer(path)
    if serializer_class is not None:
        _SERIALIZERS[name] = serializer_class


def _import_serializer(path):
    module_path, class_name = path.rsplit('.', 1)
    module = get_module(module_path, ignore_internal_errors=True)
    return getattr(module, class_name, None)


def _load_serializers():
    global _SERIALIZERS
    serializers = {}

    for name, path in six.iteritems(BUILTIN_SERIALIZERS):
        serializer_class = _import_serializer(path)
        if serializer_class is not None:
            serializers[name] = serializer_class

    if hasattr(settings, 'DATA_SERIALIZERS'):
        for name, path in six.iteritems(settings.DATA_SERIALIZERS):
            serializer_class = _import_serializer(path)
            if serializer_class is not None:
                serializers[name] = serializer_class

    _SERIALIZERS = serializers

