# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from django.utils import six

from yepes.conf import settings
from yepes.utils.modules import import_module

BUILTIN_SERIALIZERS = {
    'csv': 'yepes.contrib.datamigrations.serializers.csv.CsvSerializer',
    'json': 'yepes.contrib.datamigrations.serializers.json.JsonSerializer',
    'tsv': 'yepes.contrib.datamigrations.serializers.tsv.TsvSerializer',
    'yaml': 'yepes.contrib.datamigrations.serializers.yaml.YamlSerializer',
}

_SERIALIZERS = None


MissingSerializerError = LookupError


def serialize(format, headers, data, file=None, **parameters):
    s = get_serializer(format)(**parameters)
    return s.serialize(headers, data, file)


def deserialize(format, headers, source, **parameters):
    s = get_serializer(format)(**parameters)
    return s.deserialize(headers, source)


def get_serializer(name):
    if not has_serializer(name):
        msg = "Serializer '{0}' could not be found."
        raise LookupError(msg.format(name))
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
    module = import_module(module_path, ignore_internal_errors=True)
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

