# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from django import test

from yepes.contrib.datamigrations.serializers import (
    serializers,
    SerializerRegistry,
)
from yepes.contrib.datamigrations.serializers.csv import CsvSerializer
from yepes.contrib.datamigrations.serializers.json import JsonSerializer
from yepes.contrib.datamigrations.serializers.tsv import TsvSerializer
from yepes.contrib.datamigrations.serializers.xls import XlsSerializer
from yepes.contrib.datamigrations.serializers.xlsx import XlsxSerializer
from yepes.contrib.datamigrations.serializers.yaml import YamlSerializer


class SerializerRegistryTests(test.TestCase):

    maxDiff = None

    def setUp(self):
        super(SerializerRegistryTests, self).setUp()
        self.assertEqual('csv', CsvSerializer.name)
        self.assertEqual('json', JsonSerializer.name)
        self.assertEqual('tsv', TsvSerializer.name)
        self.assertEqual('xls', XlsSerializer.name)
        self.assertEqual('xlsx', XlsxSerializer.name)
        self.assertEqual('yaml', YamlSerializer.name)

    def test_registry_class(self):
        registry = SerializerRegistry()
        self.assertEqual(
                set(),
                set(registry.get_serializers()))

        self.assertTrue(
                registry.register_serializer(CsvSerializer))
        self.assertEqual(
                {CsvSerializer},
                set(registry.get_serializers()))

        self.assertTrue(
                registry.register_serializer('yepes.contrib.datamigrations.serializers.json.JsonSerializer'))
        self.assertEqual(
                {CsvSerializer, JsonSerializer},
                set(registry.get_serializers()))

        self.assertFalse(
                registry.register_serializer('yepes.contrib.datamigrations.serializers.json.MissingSerializer'))
        self.assertEqual(
                {CsvSerializer, JsonSerializer},
                set(registry.get_serializers()))

        self.assertTrue('csv' in registry)
        self.assertTrue('json' in registry)
        self.assertFalse('yaml' in registry)
        self.assertTrue(registry.has_serializer('csv'))
        self.assertTrue(registry.has_serializer('json'))
        self.assertFalse(registry.has_serializer('yaml'))
        self.assertIs(registry.get_serializer('csv'), CsvSerializer)
        self.assertIs(registry.get_serializer('json'), JsonSerializer)
        with self.assertRaisesRegexp(LookupError, "Serializer 'yaml' could not be found."):
            registry.get_serializer('yaml')

    def test_default_registry_object(self):
        self.assertEqual(
            {
                CsvSerializer, JsonSerializer, TsvSerializer,
                XlsSerializer, XlsxSerializer, YamlSerializer,
            },
            set(serializers.get_serializers()),
        )
        self.assertTrue('csv' in serializers)
        self.assertTrue('json' in serializers)
        self.assertTrue('tsv' in serializers)
        self.assertTrue('xls' in serializers)
        self.assertTrue('xlsx' in serializers)
        self.assertTrue('yaml' in serializers)

