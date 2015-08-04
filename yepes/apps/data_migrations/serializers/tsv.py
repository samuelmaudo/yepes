# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from django.utils.six import PY3

from yepes.apps.data_migrations.serializers.csv import CsvSerializer


class TsvSerializer(CsvSerializer):

    def __init__(self, **serializer_parameters):
        defaults = {
            'delimiter': '\t' if PY3 else b'\t',
        }
        defaults.update(serializer_parameters)
        super(TsvSerializer, self).__init__(**defaults)

