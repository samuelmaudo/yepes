# -*- coding:utf-8 -*-

from __future__ import absolute_import, unicode_literals

from json import JSONDecoder, JSONEncoder

from django.utils.six import PY3
from django.utils.six.moves import zip

from yepes.data_migrations.serializers.base import Serializer
from yepes.types import Undefined

class JsonSerializer(Serializer):

    def __init__(self, **serializer_parameters):
        defaults = {
            'ensure_ascii': False,
            'indent': '',
        }
        defaults.update(serializer_parameters)
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

        if not PY3:
            headers = [h.encode('utf8', 'replace') for h in headers]
            indent = None if indent is None else indent.encode('utf8', 'replace')
            newline = newline.encode('utf8', 'replace')
            newline_indent = newline_indent.encode('utf8', 'replace')
            data_begin = data_begin.encode('utf8', 'replace')
            data_end = data_end.encode('utf8', 'replace')
            item_separator = item_separator.encode('utf8', 'replace')
            key_wrapper = key_wrapper.encode('utf8', 'replace')
            key_separator = key_separator.encode('utf8', 'replace')
            row_begin = row_begin.encode('utf8', 'replace')
            row_end = row_end.encode('utf8', 'replace')
            row_separator = row_separator.encode('utf8', 'replace')

        # Function shortcuts
        write = file.write
        serialize = encoder.encode

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
                if not PY3:
                    serialized_value = serialized_value.encode('utf8', 'replace')

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

