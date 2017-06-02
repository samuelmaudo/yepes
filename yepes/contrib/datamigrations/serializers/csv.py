# -*- coding:utf-8 -*-

from __future__ import absolute_import, unicode_literals

from django.utils.six import PY2

if PY2:
    import unicodecsv as csv
else:
    import csv

from yepes.contrib.datamigrations.serializers import Serializer
from yepes.contrib.datamigrations.constants import FLOAT, INTEGER, TEXT
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
    is_binary = True if PY2 else False

    def __init__(self, **serializer_parameters):
        defaults = {
            'delimiter': ',',
            'doublequote': True,
            'lineterminator': '\r\n',
            'nonereplacement': '\\N',
            'quotechar': '"',
            'quoting': csv.QUOTE_MINIMAL,
            'skipinitialspace': False,
        }
        defaults.update(serializer_parameters)

        if PY2:

            delimiter = defaults['delimiter']
            if isinstance(delimiter, unicode):
                defaults['delimiter'] = delimiter.encode()

            lineterminator = defaults['lineterminator']
            if isinstance(lineterminator, unicode):
                defaults['lineterminator'] = lineterminator.encode()

            nonereplacement = defaults['nonereplacement']
            if isinstance(nonereplacement, unicode):
                defaults['nonereplacement'] = nonereplacement.encode()

            quotechar = defaults['quotechar']
            if isinstance(quotechar, unicode):
                defaults['quotechar'] = quotechar.encode()

        elif defaults.get('newline') is None:

            defaults['newline'] = ''

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

