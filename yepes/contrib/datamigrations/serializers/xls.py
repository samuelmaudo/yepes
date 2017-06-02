# -*- coding:utf-8 -*-

from __future__ import absolute_import, unicode_literals

from xlrd import open_workbook
from xlwt import Workbook

from django.utils.six.moves import range

from yepes.contrib.datamigrations.serializers import Serializer
from yepes.types import Undefined


class XlsSerializer(Serializer):

    is_binary = True

    def __init__(self, **serializer_parameters):
        serializer_parameters.setdefault('nonereplacement', '\\N')
        super(XlsSerializer, self).__init__(**serializer_parameters)

    def dump(self, headers, data, file):
        workbook = Workbook()
        worksheet = workbook.add_sheet('Data')
        for col, header in enumerate(headers):
            worksheet.write(0, col, header)

        for row, values in enumerate(data, 1):
            for col, value in enumerate(values):
                worksheet.write(row, col, value)

        workbook.save(file)

    def load(self, headers, file):
        workbook = open_workbook(file_contents=file.read())
        worksheet = workbook.sheet_by_index(0)

        columns = list(range(worksheet.ncols))
        first_line = [
            worksheet.cell_value(0, col)
            for col
            in columns
        ]
        if first_line != headers:
            del columns[:]
            for header in headers:
                try:
                    col = first_line.index(header)
                except ValueError:
                    col = None

                columns.append(col)

        return (
            [
                Undefined if col is None else worksheet.cell_value(row, col)
                for col
                in columns
            ]
            for row
            in range(1, worksheet.nrows)
        )

