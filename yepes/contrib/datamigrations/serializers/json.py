# -*- coding:utf-8 -*-

from __future__ import absolute_import, unicode_literals

from json import JSONDecoder, JSONEncoder

from django.utils.six import PY2
from django.utils.six.moves import zip

from yepes.contrib.datamigrations.serializers import Serializer
from yepes.types import Undefined

class JsonSerializer(Serializer):

    def __init__(self, **serializer_parameters):
        defaults = {
            'ensure_ascii': False,
            'indent': '',
            'separators': (', ', ': '),
        }
        defaults.update(serializer_parameters)

        # In Python 2 it is easy to mix unicode and binary strings
        # but from Python 3 developers must ensure that all input
        # values are unicode strings.
        if PY2:
            indent = defaults['indent']
            if isinstance(indent, bytes):
                defaults['indent'] = indent.decode()

            defaults['separators'] = tuple(
                separator.decode() if isinstance(separator, bytes) else separator
                for separator
                in defaults['separators']
            )

        super(JsonSerializer, self).__init__(**defaults)

    def dump(self, headers, data, file):
        encoder = JSONEncoder(**self.serializer_parameters)

        # JSON pieces
        indent = encoder.indent
        newline = '\n'
        newline_indent = '' if indent is None else newline + indent
        data_begin = '['
        data_end = ']'
        item_separator = encoder.item_separator
        key_wrapper = '"'
        key_separator = encoder.key_separator
        row_begin = '{'
        row_end = '}'
        row_separator = item_separator if indent is None else item_separator.rstrip()

        # Function shortcuts
        write = file.write
        serialize = encoder.encode

        # Binary decoding
        if PY2:
            headers = [
                key.decode() if isinstance(key, bytes) else key
                for key
                in headers
            ]
            def serialize(value):
                string = encoder.encode(value)
                if isinstance(string, bytes):
                    string = string.decode()
                return string

        # Data writing
        encoder.indent = None
        write(data_begin)
        first_row = True
        for row in data:
            if not first_row:
                write(row_separator)

            write(newline_indent)
            write(row_begin)
            first_item = True
            for key, value in zip(headers, row):
                if not first_item:
                    write(item_separator)

                write(key_wrapper)
                write(key)
                write(key_wrapper)
                write(key_separator)

                serialized_value = serialize(value)

                write(serialized_value)
                first_item = False

            write(row_end)
            first_row = False

        if indent is not None:
            write(newline)

        write(data_end)
        encoder.indent = indent

    def load(self, headers, file):
        json = JSONDecoder(self.serializer_parameters.get('encoding'))
        return (
            [
                object.get(header, Undefined)
                for header
                in headers
            ]
            for object
            in json.decode(file.read())
        )

