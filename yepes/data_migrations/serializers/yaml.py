# -*- coding:utf-8 -*-

from __future__ import absolute_import, unicode_literals

from types import GeneratorType
try:
    from yaml import CSafeLoader as YamlLoader, CSafeDumper as YamlDumper
except ImportError:
    from yaml import SafeLoader as YamlLoader, SafeDumper as YamlDumper

from django.utils.six import PY3
from django.utils.six.moves import zip

from yepes.data_migrations.serializers.base import Serializer
from yepes.types import Undefined

YamlDumper.add_representer(GeneratorType, YamlDumper.represent_list)


class YamlSerializer(Serializer):

    def __init__(self, **serializer_parameters):
        defaults = {
            'allow_unicode': True,
            'encoding': None if PY3 else 'utf-8',
            'explicit_end': False,
            'explicit_start': False,
            'width': 1000,
        }
        defaults.update(serializer_parameters)
        super(YamlSerializer, self).__init__(**defaults)

    def dump(self, headers, data, file):
        dumper = YamlDumper(file, **self.serializer_parameters)
        try:
            dumper.open()
            dumper.represent((
                {
                    k: v
                    for k,v
                    in zip(headers, row)
                }
                for row
                in data
            ))
            dumper.close()
        finally:
            dumper.dispose()


    def load(self, headers, file):
        loader = YamlLoader(file)
        return (
            [
                object.get(header, Undefined)
                for header
                in headers
            ]
            for object
            in loader.get_data()
        )

