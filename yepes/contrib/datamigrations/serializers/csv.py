# -*- coding:utf-8 -*-

from __future__ import absolute_import, unicode_literals

from django.utils.six import PY3

if PY3:
    import csv
else:
    import unicodecsv as csv

from yepes.contrib.datamigrations.serializers import Serializer
from yepes.contrib.datamigrations.types import FLOAT, INTEGER, TEXT
from yepes.types import Undefined


class CsvSerializer(Serializer):

    exportation_data_types = frozenset([
        TEXT,
        INTEGER,
        FLOAT,
    ])
    importation_data_types = frozenset([
        TEXT,
    ])

    def __init__(self, **serializer_parameters):
        defaults = {
            'delimiter': ',' if PY3 else b',',
            'doublequote': True,
            'lineterminator': '\r\n' if PY3 else b'\r\n',
            'nonereplacement': '\\N' if PY3 else b'\\N',
            'quotechar': '"' if PY3 else b'"',
            'quoting': csv.QUOTE_MINIMAL,
            'skipinitialspace': False,
        }
        defaults.update(serializer_parameters)
        super(CsvSerializer, self).__init__(**defaults)

    def dump(self, headers, data, file):
        writer = csv.writer(file, **self.serializer_parameters)
        writer.writerow(headers)
        writer.writerows(data)

    def load(self, headers, file):
        reader = csv.reader(file, **self.serializer_parameters)
        first_line = next(reader)
        if first_line == headers:
            return reader

        positions = []
        for header in headers:
            try:
                pos = first_line.index(header)
            except ValueError:
                pos = None

            positions.append(pos)

        return (
            [
                Undefined if pos is None else row[pos]
                for pos
                in positions
            ]
            for row
            in reader
        )

