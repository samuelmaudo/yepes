# -*- coding:utf-8 -*-

from __future__ import unicode_literals

import csv
from datetime import date, datetime, time
from decimal import Decimal
from io import open
import os
from unittest import expectedFailure
import warnings

from django import test
from django.test.utils import override_settings
from django.utils import six
from django.utils._os import upath
from django.utils.six.moves import zip
from django.utils.timezone import utc as UTC

from yepes.contrib.datamigrations.importation_plans.direct import DirectPlan
from yepes.contrib.datamigrations.importation_plans.replace_all import ReplaceAllPlan
from yepes.contrib.datamigrations.serializers.csv import CsvSerializer
from yepes.contrib.datamigrations.serializers.json import JsonSerializer
from yepes.contrib.datamigrations.serializers.tsv import TsvSerializer
from yepes.contrib.datamigrations.serializers.xls import XlsSerializer
from yepes.contrib.datamigrations.serializers.xlsx import XlsxSerializer
from yepes.contrib.datamigrations.serializers.yaml import YamlSerializer
from yepes.test_mixins import TempDirMixin

from .data_migrations import (
    BooleanMigration,
    DateTimeMigration,
    DateTimeEdgeMigration,
    FileMigration,
    NumericMigration,
    TextMigration,
)
from .models import (
    BooleanModel,
    DateTimeModel,
    FileModel,
    NumericModel,
    TextModel,
)

MODULE_DIR = os.path.abspath(os.path.dirname(upath(__file__)))
MIGRATIONS_DIR = os.path.join(MODULE_DIR, 'data_migrations')


class BooleanFieldsTests(TempDirMixin, test.TestCase):

    expectedResults = [
        (True, True),
        (True, True),
        (True, True),
        (True, True),
        (False, False),
        (False, False),
        (False, False),
        (False, False),
        (True, None),
        (False, None),
    ]
    maxDiff = None
    tempDirPrefix = 'test_data_migrations_'

    def test_data_migration(self):
        migration = BooleanMigration(BooleanModel)
        self.assertEqual(
            [repr(fld) for fld in migration.fields],
            ['<yepes.contrib.datamigrations.fields.BooleanField: boolean>',
             '<yepes.contrib.datamigrations.fields.BooleanField: boolean_as_string>',
             '<yepes.contrib.datamigrations.fields.BooleanField: null_boolean>',
             '<yepes.contrib.datamigrations.fields.BooleanField: null_boolean_as_string>'],
        )
        self.assertEqual(
            [repr(fld) for fld in migration.fields_to_import],
            ['<yepes.contrib.datamigrations.fields.BooleanField: boolean>',
             '<yepes.contrib.datamigrations.fields.BooleanField: boolean_as_string>',
             '<yepes.contrib.datamigrations.fields.BooleanField: null_boolean>',
             '<yepes.contrib.datamigrations.fields.BooleanField: null_boolean_as_string>'],
        )
        self.assertIsNone(migration.primary_key)
        self.assertIsNone(migration.natural_foreign_keys)
        self.assertTrue(migration.can_create)
        self.assertFalse(migration.can_update)
        self.assertFalse(migration.requires_model_instances)

    def test_csv_serializer(self):
        migration = BooleanMigration(BooleanModel)
        import_serializer = CsvSerializer()
        export_serializer = CsvSerializer(quoting=csv.QUOTE_NONNUMERIC)

        source_path = os.path.join(MIGRATIONS_DIR, 'boolean_source.csv')
        expected_path = os.path.join(MIGRATIONS_DIR, 'boolean_result.csv')
        result_path = os.path.join(self.temp_dir, 'boolean_result.csv')

        # Import data from a string.
        with import_serializer.open_to_load(source_path) as source_file:
            migration.import_data(source_file.read(), import_serializer, DirectPlan)

        objs = list(BooleanModel.objects.all())
        self.assertEqual(len(objs), len(self.expectedResults))
        for obj, result in zip(objs, self.expectedResults):
            self.assertEqual(obj.boolean, result[0])
            self.assertEqual(obj.boolean_as_string, result[0])
            self.assertEqual(obj.null_boolean, result[1])
            self.assertEqual(obj.null_boolean_as_string, result[1])

        # Export data to a string.
        result = migration.export_data(serializer=export_serializer)

        with import_serializer.open_to_load(expected_path) as expected_file:
            self.assertEqual(
                    result.splitlines(),
                    expected_file.read().splitlines())

        # Import data from a file.
        with import_serializer.open_to_load(source_path) as source_file:
            migration.import_data(source_file, import_serializer, ReplaceAllPlan)

        objs = list(BooleanModel.objects.all())
        self.assertEqual(len(objs), len(self.expectedResults))
        for obj, result in zip(objs, self.expectedResults):
            self.assertEqual(obj.boolean, result[0])
            self.assertEqual(obj.boolean_as_string, result[0])
            self.assertEqual(obj.null_boolean, result[1])
            self.assertEqual(obj.null_boolean_as_string, result[1])

        # Export data to a file.
        with export_serializer.open_to_dump(result_path) as result_file:
            migration.export_data(result_file, export_serializer)

        with open(expected_path, 'rt') as expected_file:
            with open(result_path, 'rt') as result_file:
                self.assertEqual(
                        result_file.read().splitlines(),
                        expected_file.read().splitlines())

    def test_json_serializer(self):
        migration = BooleanMigration(BooleanModel)
        serializer = JsonSerializer()

        source_path = os.path.join(MIGRATIONS_DIR, 'boolean_source.json')
        expected_path = os.path.join(MIGRATIONS_DIR, 'boolean_result.json')
        result_path = os.path.join(self.temp_dir, 'boolean_result.json')

        # Import data from a string.
        with serializer.open_to_load(source_path) as source_file:
            migration.import_data(source_file.read(), serializer, DirectPlan)

        objs = list(BooleanModel.objects.all())
        self.assertEqual(len(objs), len(self.expectedResults))
        for obj, result in zip(objs, self.expectedResults):
            self.assertEqual(obj.boolean, result[0])
            self.assertEqual(obj.boolean_as_string, result[0])
            self.assertEqual(obj.null_boolean, result[1])
            self.assertEqual(obj.null_boolean_as_string, result[1])

        # Export data to a string.
        result = migration.export_data(serializer=serializer)

        with open(expected_path, 'rt') as expected_file:
            self.assertEqual(
                    result.splitlines(),
                    expected_file.read().splitlines())

        # Import data from a file.
        with serializer.open_to_load(source_path) as source_file:
            migration.import_data(source_file, serializer, ReplaceAllPlan)

        objs = list(BooleanModel.objects.all())
        self.assertEqual(len(objs), len(self.expectedResults))
        for obj, result in zip(objs, self.expectedResults):
            self.assertEqual(obj.boolean, result[0])
            self.assertEqual(obj.boolean_as_string, result[0])
            self.assertEqual(obj.null_boolean, result[1])
            self.assertEqual(obj.null_boolean_as_string, result[1])

        # Export data to a file.
        with serializer.open_to_dump(result_path) as result_file:
            migration.export_data(result_file, serializer)

        with open(expected_path, 'rt') as expected_file:
            with open(result_path, 'rt') as result_file:
                self.assertEqual(
                        result_file.read().splitlines(),
                        expected_file.read().splitlines())

    def test_tsv_serializer(self):
        migration = BooleanMigration(BooleanModel)
        import_serializer = TsvSerializer()
        export_serializer = TsvSerializer(quoting=csv.QUOTE_NONNUMERIC)

        source_path = os.path.join(MIGRATIONS_DIR, 'boolean_source.tsv')
        expected_path = os.path.join(MIGRATIONS_DIR, 'boolean_result.tsv')
        result_path = os.path.join(self.temp_dir, 'boolean_result.tsv')

        # Import data from a string.
        with import_serializer.open_to_load(source_path) as source_file:
            migration.import_data(source_file.read(), import_serializer, DirectPlan)

        objs = list(BooleanModel.objects.all())
        self.assertEqual(len(objs), len(self.expectedResults))
        for obj, result in zip(objs, self.expectedResults):
            self.assertEqual(obj.boolean, result[0])
            self.assertEqual(obj.boolean_as_string, result[0])
            self.assertEqual(obj.null_boolean, result[1])
            self.assertEqual(obj.null_boolean_as_string, result[1])

        # Export data to a string.
        result = migration.export_data(serializer=export_serializer)

        with import_serializer.open_to_load(expected_path) as expected_file:
            self.assertEqual(
                    result.splitlines(),
                    expected_file.read().splitlines())

        # Import data from a file.
        with import_serializer.open_to_load(source_path) as source_file:
            migration.import_data(source_file, import_serializer, ReplaceAllPlan)

        objs = list(BooleanModel.objects.all())
        self.assertEqual(len(objs), len(self.expectedResults))
        for obj, result in zip(objs, self.expectedResults):
            self.assertEqual(obj.boolean, result[0])
            self.assertEqual(obj.boolean_as_string, result[0])
            self.assertEqual(obj.null_boolean, result[1])
            self.assertEqual(obj.null_boolean_as_string, result[1])

        # Export data to a file.
        with export_serializer.open_to_dump(result_path) as result_file:
            migration.export_data(result_file, export_serializer)

        with open(expected_path, 'rt') as expected_file:
            with open(result_path, 'rt') as result_file:
                self.assertEqual(
                        result_file.read().splitlines(),
                        expected_file.read().splitlines())

    def test_xls_serializer(self):
        migration = BooleanMigration(BooleanModel)
        import_serializer = CsvSerializer()
        export_serializer = CsvSerializer(quoting=csv.QUOTE_NONNUMERIC)
        binary_serializer = XlsSerializer()

        source_path = os.path.join(MIGRATIONS_DIR, 'boolean_source.csv')
        expected_path = os.path.join(MIGRATIONS_DIR, 'boolean_result.csv')
        result_path = os.path.join(self.temp_dir, 'boolean_result.csv')
        binary_path = os.path.join(self.temp_dir, 'boolean_result.xls')

        # Load initial data with a text serializer.
        with import_serializer.open_to_load(source_path) as source_file:
            migration.import_data(source_file, import_serializer, DirectPlan)

        objs = list(BooleanModel.objects.all())
        self.assertEqual(len(objs), len(self.expectedResults))
        for obj, result in zip(objs, self.expectedResults):
            self.assertEqual(obj.boolean, result[0])
            self.assertEqual(obj.boolean_as_string, result[0])
            self.assertEqual(obj.null_boolean, result[1])
            self.assertEqual(obj.null_boolean_as_string, result[1])

        # Export and import data with the binary serializer (replacing
        # previous data).
        binary_result = migration.export_data(serializer=binary_serializer)
        self.assertIsInstance(binary_result, six.binary_type)
        migration.import_data(binary_result, binary_serializer, ReplaceAllPlan)

        # Export resulting data with the text serializer and compare it
        # with the expected file.
        with export_serializer.open_to_dump(result_path) as result_file:
            migration.export_data(result_file, export_serializer)

        with open(expected_path, 'rt') as expected_file:
            with open(result_path, 'rt') as result_file:
                self.assertEqual(
                        result_file.read().splitlines(),
                        expected_file.read().splitlines())

        # Repeat the process using files instead of strings.
        with binary_serializer.open_to_dump(binary_path) as binary_file:
            migration.export_data(binary_file, binary_serializer)

        with binary_serializer.open_to_load(binary_path) as binary_file:
            migration.import_data(binary_file, binary_serializer, ReplaceAllPlan)

        with export_serializer.open_to_dump(result_path) as result_file:
            migration.export_data(result_file, export_serializer)

        with open(expected_path, 'rt') as expected_file:
            with open(result_path, 'rt') as result_file:
                self.assertEqual(
                        result_file.read().splitlines(),
                        expected_file.read().splitlines())

    def test_xlsx_serializer(self):
        migration = BooleanMigration(BooleanModel)
        import_serializer = CsvSerializer()
        export_serializer = CsvSerializer(quoting=csv.QUOTE_NONNUMERIC)
        binary_serializer = XlsxSerializer()

        source_path = os.path.join(MIGRATIONS_DIR, 'boolean_source.csv')
        expected_path = os.path.join(MIGRATIONS_DIR, 'boolean_result.csv')
        result_path = os.path.join(self.temp_dir, 'boolean_result.csv')
        binary_path = os.path.join(self.temp_dir, 'boolean_result.xlsx')

        # Load initial data with a text serializer.
        with import_serializer.open_to_load(source_path) as source_file:
            migration.import_data(source_file, import_serializer, DirectPlan)

        objs = list(BooleanModel.objects.all())
        self.assertEqual(len(objs), len(self.expectedResults))
        for obj, result in zip(objs, self.expectedResults):
            self.assertEqual(obj.boolean, result[0])
            self.assertEqual(obj.boolean_as_string, result[0])
            self.assertEqual(obj.null_boolean, result[1])
            self.assertEqual(obj.null_boolean_as_string, result[1])

        # Export and import data with the binary serializer (replacing
        # previous data).
        binary_result = migration.export_data(serializer=binary_serializer)
        self.assertIsInstance(binary_result, six.binary_type)
        migration.import_data(binary_result, binary_serializer, ReplaceAllPlan)

        # Export resulting data with the text serializer and compare it
        # with the expected file.
        with export_serializer.open_to_dump(result_path) as result_file:
            migration.export_data(result_file, export_serializer)

        with open(expected_path, 'rt') as expected_file:
            with open(result_path, 'rt') as result_file:
                self.assertEqual(
                        result_file.read().splitlines(),
                        expected_file.read().splitlines())

        # Repeat the process using files instead of strings.
        with binary_serializer.open_to_dump(binary_path) as binary_file:
            migration.export_data(binary_file, binary_serializer)

        with binary_serializer.open_to_load(binary_path) as binary_file:
            migration.import_data(binary_file, binary_serializer, ReplaceAllPlan)

        with export_serializer.open_to_dump(result_path) as result_file:
            migration.export_data(result_file, export_serializer)

        with open(expected_path, 'rt') as expected_file:
            with open(result_path, 'rt') as result_file:
                self.assertEqual(
                        result_file.read().splitlines(),
                        expected_file.read().splitlines())

    def test_yaml_serializer(self):
        migration = BooleanMigration(BooleanModel)
        serializer = YamlSerializer()

        source_path = os.path.join(MIGRATIONS_DIR, 'boolean_source.yaml')
        expected_path = os.path.join(MIGRATIONS_DIR, 'boolean_result.yaml')
        result_path = os.path.join(self.temp_dir, 'boolean_result.yaml')

        # Import data from a string.
        with serializer.open_to_load(source_path) as source_file:
            migration.import_data(source_file.read(), serializer, DirectPlan)

        objs = list(BooleanModel.objects.all())
        self.assertEqual(len(objs), len(self.expectedResults))
        for obj, result in zip(objs, self.expectedResults):
            self.assertEqual(obj.boolean, result[0])
            self.assertEqual(obj.boolean_as_string, result[0])
            self.assertEqual(obj.null_boolean, result[1])
            self.assertEqual(obj.null_boolean_as_string, result[1])

        # Export data to a string.
        result = migration.export_data(serializer=serializer)

        with open(expected_path, 'rt') as expected_file:
            self.assertEqual(
                    result.splitlines(),
                    expected_file.read().splitlines())

        # Import data from a file.
        with serializer.open_to_load(source_path) as source_file:
            migration.import_data(source_file, serializer, ReplaceAllPlan)

        objs = list(BooleanModel.objects.all())
        self.assertEqual(len(objs), len(self.expectedResults))
        for obj, result in zip(objs, self.expectedResults):
            self.assertEqual(obj.boolean, result[0])
            self.assertEqual(obj.boolean_as_string, result[0])
            self.assertEqual(obj.null_boolean, result[1])
            self.assertEqual(obj.null_boolean_as_string, result[1])

        # Export data to a file.
        with serializer.open_to_dump(result_path) as result_file:
            migration.export_data(result_file, serializer)

        with open(expected_path, 'rt') as expected_file:
            with open(result_path, 'rt') as result_file:
                self.assertEqual(
                        result_file.read().splitlines(),
                        expected_file.read().splitlines())


@override_settings(TIME_ZONE='Atlantic/South_Georgia')
class DateTimeFieldsTests(TempDirMixin, test.TestCase):

    expectedResults = [
        (date(1986, 9, 25), datetime(1986, 9, 25, 14, 0, 34, tzinfo=UTC), time(12, 0, 34)),
        (date(1986, 9, 25), datetime(1986, 9, 25, 14, 0, 34, 123456, UTC), time(12, 0, 34, 123456)),
        (date(1986, 9, 25), datetime(1986, 9, 25, 12, 0, 34, 123456, UTC), time(12, 0, 34, 123456)),
        (date(1986, 9, 25), datetime(1986, 9, 25, 12, 0, 34, 123456, UTC), time(12, 0, 34, 123456)),
        (date(1986, 9, 25), datetime(1986, 9, 25, 16, 30, 34, 123456, UTC), time(12, 0, 34, 123456)),
        (None, None, None),
        (None, None, None),
    ]
    maxDiff = None
    tempDirPrefix = 'test_data_migrations_'

    def test_data_migrations(self):
        migration = DateTimeMigration(DateTimeModel)
        self.assertEqual(
            [repr(fld) for fld in migration.fields],
            ['<yepes.contrib.datamigrations.fields.DateField: date>',
             '<yepes.contrib.datamigrations.fields.YearField: date__year>',
             '<yepes.contrib.datamigrations.fields.MonthField: date__month>',
             '<yepes.contrib.datamigrations.fields.DayField: date__day>',
             '<yepes.contrib.datamigrations.fields.DateTimeField: datetime>',
             '<yepes.contrib.datamigrations.fields.YearField: datetime__year>',
             '<yepes.contrib.datamigrations.fields.MonthField: datetime__month>',
             '<yepes.contrib.datamigrations.fields.DayField: datetime__day>',
             '<yepes.contrib.datamigrations.fields.HourField: datetime__hour>',
             '<yepes.contrib.datamigrations.fields.MinuteField: datetime__minute>',
             '<yepes.contrib.datamigrations.fields.SecondField: datetime__second>',
             '<yepes.contrib.datamigrations.fields.MicrosecondField: datetime__microsecond>',
             '<yepes.contrib.datamigrations.fields.TimeZoneField: datetime__tzinfo>',
             '<yepes.contrib.datamigrations.fields.TimeField: time>',
             '<yepes.contrib.datamigrations.fields.HourField: time__hour>',
             '<yepes.contrib.datamigrations.fields.MinuteField: time__minute>',
             '<yepes.contrib.datamigrations.fields.SecondField: time__second>',
             '<yepes.contrib.datamigrations.fields.MicrosecondField: time__microsecond>',
             '<yepes.contrib.datamigrations.fields.TimeZoneField: time__tzinfo>'],
        )
        self.assertEqual(
            [repr(fld) for fld in migration.fields_to_import],
            ['<yepes.contrib.datamigrations.fields.DateField: date>',
             '<yepes.contrib.datamigrations.fields.DateTimeField: datetime>',
             '<yepes.contrib.datamigrations.fields.TimeField: time>'],
        )
        self.assertIsNone(migration.primary_key)
        self.assertIsNone(migration.natural_foreign_keys)
        self.assertTrue(migration.can_create)
        self.assertFalse(migration.can_update)
        self.assertTrue(migration.requires_model_instances)

        migration = DateTimeEdgeMigration(DateTimeModel)
        self.assertEqual(
            [repr(fld) for fld in migration.fields],
            ['<yepes.contrib.datamigrations.fields.DateTimeField: date__datetime (date)>',
             '<yepes.contrib.datamigrations.fields.YearField: date__year (date)>',
             '<yepes.contrib.datamigrations.fields.MonthField: date__month (date)>',
             '<yepes.contrib.datamigrations.fields.DayField: date__day (date)>',
             '<yepes.contrib.datamigrations.fields.DateField: datetime__date (datetime)>',
             '<yepes.contrib.datamigrations.fields.TimeField: datetime__time (datetime)>',
             '<yepes.contrib.datamigrations.fields.YearField: datetime__year (datetime)>',
             '<yepes.contrib.datamigrations.fields.MonthField: datetime__month (datetime)>',
             '<yepes.contrib.datamigrations.fields.DayField: datetime__day (datetime)>',
             '<yepes.contrib.datamigrations.fields.HourField: datetime__hour (datetime)>',
             '<yepes.contrib.datamigrations.fields.MinuteField: datetime__minute (datetime)>',
             '<yepes.contrib.datamigrations.fields.SecondField: datetime__second (datetime)>',
             '<yepes.contrib.datamigrations.fields.MicrosecondField: datetime__microsecond (datetime)>',
             '<yepes.contrib.datamigrations.fields.TimeZoneField: datetime__tzinfo (datetime)>',
             '<yepes.contrib.datamigrations.fields.HourField: time__hour (time)>',
             '<yepes.contrib.datamigrations.fields.MinuteField: time__minute (time)>',
             '<yepes.contrib.datamigrations.fields.SecondField: time__second (time)>',
             '<yepes.contrib.datamigrations.fields.MicrosecondField: time__microsecond (time)>',
             '<yepes.contrib.datamigrations.fields.TimeZoneField: time__tzinfo (time)>'],
        )
        self.assertEqual(
            [repr(fld) for fld in migration.fields_to_import],
            ['<yepes.contrib.datamigrations.fields.DateTimeField: date__datetime (date)>',
             '<yepes.contrib.datamigrations.fields.YearField: date__year (date)>',
             '<yepes.contrib.datamigrations.fields.MonthField: date__month (date)>',
             '<yepes.contrib.datamigrations.fields.DayField: date__day (date)>',
             '<yepes.contrib.datamigrations.fields.DateField: datetime__date (datetime)>',
             '<yepes.contrib.datamigrations.fields.TimeField: datetime__time (datetime)>',
             '<yepes.contrib.datamigrations.fields.YearField: datetime__year (datetime)>',
             '<yepes.contrib.datamigrations.fields.MonthField: datetime__month (datetime)>',
             '<yepes.contrib.datamigrations.fields.DayField: datetime__day (datetime)>',
             '<yepes.contrib.datamigrations.fields.HourField: datetime__hour (datetime)>',
             '<yepes.contrib.datamigrations.fields.MinuteField: datetime__minute (datetime)>',
             '<yepes.contrib.datamigrations.fields.SecondField: datetime__second (datetime)>',
             '<yepes.contrib.datamigrations.fields.MicrosecondField: datetime__microsecond (datetime)>',
             '<yepes.contrib.datamigrations.fields.TimeZoneField: datetime__tzinfo (datetime)>',
             '<yepes.contrib.datamigrations.fields.HourField: time__hour (time)>',
             '<yepes.contrib.datamigrations.fields.MinuteField: time__minute (time)>',
             '<yepes.contrib.datamigrations.fields.SecondField: time__second (time)>',
             '<yepes.contrib.datamigrations.fields.MicrosecondField: time__microsecond (time)>',
             '<yepes.contrib.datamigrations.fields.TimeZoneField: time__tzinfo (time)>'],
        )
        self.assertIsNone(migration.primary_key)
        self.assertIsNone(migration.natural_foreign_keys)
        self.assertTrue(migration.can_create)
        self.assertFalse(migration.can_update)
        self.assertFalse(migration.requires_model_instances)

    def test_csv_serializer(self):
        migration = DateTimeMigration(DateTimeModel)
        import_serializer = CsvSerializer()
        export_serializer = CsvSerializer(quoting=csv.QUOTE_NONNUMERIC)

        source_path = os.path.join(MIGRATIONS_DIR, 'datetime_source.csv')
        expected_path = os.path.join(MIGRATIONS_DIR, 'datetime_result.csv')
        result_path = os.path.join(self.temp_dir, 'datetime_result.csv')

        # Import data from a string.
        with import_serializer.open_to_load(source_path) as source_file:

            with warnings.catch_warnings(record=True) as w:
                warnings.filterwarnings('ignore', 'naive datetime')
                migration.import_data(source_file.read(), import_serializer, DirectPlan)

        objs = list(DateTimeModel.objects.all())
        self.assertEqual(len(objs), len(self.expectedResults))
        for obj, result in zip(objs, self.expectedResults):
            self.assertEqual(obj.date, result[0])
            self.assertEqual(obj.datetime, result[1])
            self.assertEqual(obj.time, result[2])

        # Export data to a string.
        result = migration.export_data(serializer=export_serializer)

        with import_serializer.open_to_load(expected_path) as expected_file:
            self.assertEqual(
                    result.splitlines(),
                    expected_file.read().splitlines())

        # Import data from a file.
        with import_serializer.open_to_load(source_path) as source_file:

            with warnings.catch_warnings(record=True) as w:
                warnings.filterwarnings('ignore', 'naive datetime')
                migration.import_data(source_file, import_serializer, ReplaceAllPlan)

        objs = list(DateTimeModel.objects.all())
        self.assertEqual(len(objs), len(self.expectedResults))
        for obj, result in zip(objs, self.expectedResults):
            self.assertEqual(obj.date, result[0])
            self.assertEqual(obj.datetime, result[1])
            self.assertEqual(obj.time, result[2])

        # Export data to a file.
        with export_serializer.open_to_dump(result_path) as result_file:
            migration.export_data(result_file, export_serializer)

        with open(expected_path, 'rt') as expected_file:
            with open(result_path, 'rt') as result_file:
                self.assertEqual(
                        result_file.read().splitlines(),
                        expected_file.read().splitlines())

        # Test edge cases.
        migration = DateTimeEdgeMigration(DateTimeModel)
        expected_path = os.path.join(MIGRATIONS_DIR, 'datetime_edge_result.csv')
        result_path = os.path.join(self.temp_dir, 'datetime_edge_result.csv')
        with export_serializer.open_to_dump(result_path) as result_file:
            migration.export_data(result_file, export_serializer)

        with open(expected_path, 'rt') as expected_file:
            with open(result_path, 'rt') as result_file:
                self.assertEqual(
                        result_file.read().splitlines(),
                        expected_file.read().splitlines())

    def test_json_serializer(self):
        migration = DateTimeMigration(DateTimeModel)
        serializer = JsonSerializer()

        source_path = os.path.join(MIGRATIONS_DIR, 'datetime_source.json')
        expected_path = os.path.join(MIGRATIONS_DIR, 'datetime_result.json')
        result_path = os.path.join(self.temp_dir, 'datetime_result.json')

        # Import data from a string.
        with serializer.open_to_load(source_path) as source_file:

            with warnings.catch_warnings(record=True) as w:
                warnings.filterwarnings('ignore', 'naive datetime')
                migration.import_data(source_file.read(), serializer, DirectPlan)

        objs = list(DateTimeModel.objects.all())
        self.assertEqual(len(objs), len(self.expectedResults))
        for obj, result in zip(objs, self.expectedResults):
            self.assertEqual(obj.date, result[0])
            self.assertEqual(obj.datetime, result[1])
            self.assertEqual(obj.time, result[2])

        # Export data to a string.
        result = migration.export_data(serializer=serializer)

        with open(expected_path, 'rt') as expected_file:
            self.assertEqual(
                    result.splitlines(),
                    expected_file.read().splitlines())

        # Import data from a file.
        with serializer.open_to_load(source_path) as source_file:

            with warnings.catch_warnings(record=True) as w:
                warnings.filterwarnings('ignore', 'naive datetime')
                migration.import_data(source_file, serializer, ReplaceAllPlan)

        objs = list(DateTimeModel.objects.all())
        self.assertEqual(len(objs), len(self.expectedResults))
        for obj, result in zip(objs, self.expectedResults):
            self.assertEqual(obj.date, result[0])
            self.assertEqual(obj.datetime, result[1])
            self.assertEqual(obj.time, result[2])

        # Export data to a file.
        with serializer.open_to_dump(result_path) as result_file:
            migration.export_data(result_file, serializer)

        with open(expected_path, 'rt') as expected_file:
            with open(result_path, 'rt') as result_file:
                self.assertEqual(
                        result_file.read().splitlines(),
                        expected_file.read().splitlines())

        # Test edge cases.
        migration = DateTimeEdgeMigration(DateTimeModel)
        expected_path = os.path.join(MIGRATIONS_DIR, 'datetime_edge_result.json')
        result_path = os.path.join(self.temp_dir, 'datetime_edge_result.json')
        with serializer.open_to_dump(result_path) as result_file:
            migration.export_data(result_file, serializer)

        with open(expected_path, 'rt') as expected_file:
            with open(result_path, 'rt') as result_file:
                self.assertEqual(
                        result_file.read().splitlines(),
                        expected_file.read().splitlines())

    def test_tsv_serializer(self):
        migration = DateTimeMigration(DateTimeModel)
        import_serializer = TsvSerializer()
        export_serializer = TsvSerializer(quoting=csv.QUOTE_NONNUMERIC)

        source_path = os.path.join(MIGRATIONS_DIR, 'datetime_source.tsv')
        expected_path = os.path.join(MIGRATIONS_DIR, 'datetime_result.tsv')
        result_path = os.path.join(self.temp_dir, 'datetime_result.tsv')

        # Import data from a string.
        with import_serializer.open_to_load(source_path) as source_file:

            with warnings.catch_warnings(record=True) as w:
                warnings.filterwarnings('ignore', 'naive datetime')
                migration.import_data(source_file.read(), import_serializer, DirectPlan)

        objs = list(DateTimeModel.objects.all())
        self.assertEqual(len(objs), len(self.expectedResults))
        for obj, result in zip(objs, self.expectedResults):
            self.assertEqual(obj.date, result[0])
            self.assertEqual(obj.datetime, result[1])
            self.assertEqual(obj.time, result[2])

        # Export data to a string.
        result = migration.export_data(serializer=export_serializer)

        with import_serializer.open_to_load(expected_path) as expected_file:
            self.assertEqual(
                    result.splitlines(),
                    expected_file.read().splitlines())

        # Import data from a file.
        with import_serializer.open_to_load(source_path) as source_file:

            with warnings.catch_warnings(record=True) as w:
                warnings.filterwarnings('ignore', 'naive datetime')
                migration.import_data(source_file, import_serializer, ReplaceAllPlan)

        objs = list(DateTimeModel.objects.all())
        self.assertEqual(len(objs), len(self.expectedResults))
        for obj, result in zip(objs, self.expectedResults):
            self.assertEqual(obj.date, result[0])
            self.assertEqual(obj.datetime, result[1])
            self.assertEqual(obj.time, result[2])

        # Export data to a file.
        with export_serializer.open_to_dump(result_path) as result_file:
            migration.export_data(result_file, export_serializer)

        with open(expected_path, 'rt') as expected_file:
            with open(result_path, 'rt') as result_file:
                self.assertEqual(
                        result_file.read().splitlines(),
                        expected_file.read().splitlines())

        # Test edge cases.
        migration = DateTimeEdgeMigration(DateTimeModel)
        expected_path = os.path.join(MIGRATIONS_DIR, 'datetime_edge_result.tsv')
        result_path = os.path.join(self.temp_dir, 'datetime_edge_result.tsv')
        with export_serializer.open_to_dump(result_path) as result_file:
            migration.export_data(result_file, export_serializer)

        with open(expected_path, 'rt') as expected_file:
            with open(result_path, 'rt') as result_file:
                self.assertEqual(
                        result_file.read().splitlines(),
                        expected_file.read().splitlines())

    def test_xls_serializer(self):
        migration = DateTimeMigration(DateTimeModel)
        import_serializer = CsvSerializer()
        export_serializer = CsvSerializer(quoting=csv.QUOTE_NONNUMERIC)
        binary_serializer = XlsSerializer()

        source_path = os.path.join(MIGRATIONS_DIR, 'datetime_source.csv')
        expected_path = os.path.join(MIGRATIONS_DIR, 'datetime_result.csv')
        result_path = os.path.join(self.temp_dir, 'datetime_result.csv')
        binary_path = os.path.join(self.temp_dir, 'datetime_result.xls')

        # Load initial data with a text serializer.
        with import_serializer.open_to_load(source_path) as source_file:

            with warnings.catch_warnings(record=True) as w:
                warnings.filterwarnings('ignore', 'naive datetime')
                migration.import_data(source_file, import_serializer, DirectPlan)

        objs = list(DateTimeModel.objects.all())
        self.assertEqual(len(objs), len(self.expectedResults))
        for obj, result in zip(objs, self.expectedResults):
            self.assertEqual(obj.date, result[0])
            self.assertEqual(obj.datetime, result[1])
            self.assertEqual(obj.time, result[2])

        # Export and import data with the binary serializer (replacing
        # previous data).
        binary_result = migration.export_data(serializer=binary_serializer)
        self.assertIsInstance(binary_result, six.binary_type)
        migration.import_data(binary_result, binary_serializer, ReplaceAllPlan)

        # Export resulting data with the text serializer and compare it
        # with the expected file.
        with export_serializer.open_to_dump(result_path) as result_file:
            migration.export_data(result_file, export_serializer)

        with open(expected_path, 'rt') as expected_file:
            with open(result_path, 'rt') as result_file:
                self.assertEqual(
                        result_file.read().splitlines(),
                        expected_file.read().splitlines())

        # Repeat the process using files instead of strings.
        with binary_serializer.open_to_dump(binary_path) as binary_file:
            migration.export_data(binary_file, binary_serializer)

        with binary_serializer.open_to_load(binary_path) as binary_file:
            migration.import_data(binary_file, binary_serializer, ReplaceAllPlan)

        with export_serializer.open_to_dump(result_path) as result_file:
            migration.export_data(result_file, export_serializer)

        with open(expected_path, 'rt') as expected_file:
            with open(result_path, 'rt') as result_file:
                self.assertEqual(
                        result_file.read().splitlines(),
                        expected_file.read().splitlines())

    def test_xlsx_serializer(self):
        migration = DateTimeMigration(DateTimeModel)
        import_serializer = CsvSerializer()
        export_serializer = CsvSerializer(quoting=csv.QUOTE_NONNUMERIC)
        binary_serializer = XlsxSerializer()

        source_path = os.path.join(MIGRATIONS_DIR, 'datetime_source.csv')
        expected_path = os.path.join(MIGRATIONS_DIR, 'datetime_result.csv')
        result_path = os.path.join(self.temp_dir, 'datetime_result.csv')
        binary_path = os.path.join(self.temp_dir, 'datetime_result.xlsx')

        # Load initial data with a text serializer.
        with import_serializer.open_to_load(source_path) as source_file:

            with warnings.catch_warnings(record=True) as w:
                warnings.filterwarnings('ignore', 'naive datetime')
                migration.import_data(source_file, import_serializer, DirectPlan)

        objs = list(DateTimeModel.objects.all())
        self.assertEqual(len(objs), len(self.expectedResults))
        for obj, result in zip(objs, self.expectedResults):
            self.assertEqual(obj.date, result[0])
            self.assertEqual(obj.datetime, result[1])
            self.assertEqual(obj.time, result[2])

        # Export and import data with the binary serializer (replacing
        # previous data).
        binary_result = migration.export_data(serializer=binary_serializer)
        self.assertIsInstance(binary_result, six.binary_type)
        migration.import_data(binary_result, binary_serializer, ReplaceAllPlan)

        # Export resulting data with the text serializer and compare it
        # with the expected file.
        with export_serializer.open_to_dump(result_path) as result_file:
            migration.export_data(result_file, export_serializer)

        with open(expected_path, 'rt') as expected_file:
            with open(result_path, 'rt') as result_file:
                self.assertEqual(
                        result_file.read().splitlines(),
                        expected_file.read().splitlines())

        # Repeat the process using files instead of strings.
        with binary_serializer.open_to_dump(binary_path) as binary_file:
            migration.export_data(binary_file, binary_serializer)

        with binary_serializer.open_to_load(binary_path) as binary_file:
            migration.import_data(binary_file, binary_serializer, ReplaceAllPlan)

        with export_serializer.open_to_dump(result_path) as result_file:
            migration.export_data(result_file, export_serializer)

        with open(expected_path, 'rt') as expected_file:
            with open(result_path, 'rt') as result_file:
                self.assertEqual(
                        result_file.read().splitlines(),
                        expected_file.read().splitlines())

    def test_yaml_serializer(self):
        migration = DateTimeMigration(DateTimeModel)
        serializer = YamlSerializer()

        source_path = os.path.join(MIGRATIONS_DIR, 'datetime_source.yaml')
        expected_path = os.path.join(MIGRATIONS_DIR, 'datetime_result.yaml')
        result_path = os.path.join(self.temp_dir, 'datetime_result.yaml')

        # Import data from a string.
        with serializer.open_to_load(source_path) as source_file:

            with warnings.catch_warnings(record=True) as w:
                warnings.filterwarnings('ignore', 'naive datetime')
                migration.import_data(source_file.read(), serializer, DirectPlan)

        objs = list(DateTimeModel.objects.all())
        self.assertEqual(len(objs), len(self.expectedResults))
        for obj, result in zip(objs, self.expectedResults):
            self.assertEqual(obj.date, result[0])
            self.assertEqual(obj.datetime, result[1])
            self.assertEqual(obj.time, result[2])

        # Export data to a string.
        result = migration.export_data(serializer=serializer)

        with open(expected_path, 'rt') as expected_file:
            self.assertEqual(
                    result.splitlines(),
                    expected_file.read().splitlines())

        # Import data from a file.
        with serializer.open_to_load(source_path) as source_file:

            with warnings.catch_warnings(record=True) as w:
                warnings.filterwarnings('ignore', 'naive datetime')
                migration.import_data(source_file, serializer, ReplaceAllPlan)

        objs = list(DateTimeModel.objects.all())
        self.assertEqual(len(objs), len(self.expectedResults))
        for obj, result in zip(objs, self.expectedResults):
            self.assertEqual(obj.date, result[0])
            self.assertEqual(obj.datetime, result[1])
            self.assertEqual(obj.time, result[2])

        # Export data to a file.
        with serializer.open_to_dump(result_path) as result_file:
            migration.export_data(result_file, serializer)

        with open(expected_path, 'rt') as expected_file:
            with open(result_path, 'rt') as result_file:
                self.assertEqual(
                        result_file.read().splitlines(),
                        expected_file.read().splitlines())

        # Test edge cases.
        migration = DateTimeEdgeMigration(DateTimeModel)
        expected_path = os.path.join(MIGRATIONS_DIR, 'datetime_edge_result.yaml')
        result_path = os.path.join(self.temp_dir, 'datetime_edge_result.yaml')
        with serializer.open_to_dump(result_path) as result_file:
            migration.export_data(result_file, serializer)

        with open(expected_path, 'rt') as expected_file:
            with open(result_path, 'rt') as result_file:
                self.assertEqual(
                        result_file.read().splitlines(),
                        expected_file.read().splitlines())


class FileFieldsTests(TempDirMixin, test.TestCase):

    expectedResults = [
        '860925120000',
        '150731173632',
        '',
        '',
    ]
    maxDiff = None
    tempDirPrefix = 'test_data_migrations_'

    def test_data_migration(self):
        migration = FileMigration(FileModel)
        self.assertEqual(
            [repr(fld) for fld in migration.fields],
            ['<yepes.contrib.datamigrations.fields.FileField: file>',
             '<yepes.contrib.datamigrations.fields.FileField: image>'],
        )
        self.assertEqual(
            [repr(fld) for fld in migration.fields_to_import],
            ['<yepes.contrib.datamigrations.fields.FileField: file>',
             '<yepes.contrib.datamigrations.fields.FileField: image>'],
        )
        self.assertIsNone(migration.primary_key)
        self.assertIsNone(migration.natural_foreign_keys)
        self.assertTrue(migration.can_create)
        self.assertFalse(migration.can_update)
        self.assertFalse(migration.requires_model_instances)

    def test_csv_serializer(self):
        migration = FileMigration(FileModel)
        import_serializer = CsvSerializer()
        export_serializer = CsvSerializer(quoting=csv.QUOTE_NONNUMERIC)

        source_path = os.path.join(MIGRATIONS_DIR, 'file_source.csv')
        expected_path = os.path.join(MIGRATIONS_DIR, 'file_result.csv')
        result_path = os.path.join(self.temp_dir, 'file_result.csv')

        # Import data from a string.
        with import_serializer.open_to_load(source_path) as source_file:
            migration.import_data(source_file.read(), import_serializer, DirectPlan)

        objs = list(FileModel.objects.all())
        self.assertEqual(len(objs), len(self.expectedResults))
        for obj, result in zip(objs, self.expectedResults):
            self.assertEqual(obj.file, result)
            self.assertEqual(obj.image, result)

        # Export data to a string.
        result = migration.export_data(serializer=export_serializer)

        with import_serializer.open_to_load(expected_path) as expected_file:
            self.assertEqual(
                    result.splitlines(),
                    expected_file.read().splitlines())

        # Import data from a file.
        with import_serializer.open_to_load(source_path) as source_file:
            migration.import_data(source_file, import_serializer, ReplaceAllPlan)

        objs = list(FileModel.objects.all())
        self.assertEqual(len(objs), len(self.expectedResults))
        for obj, result in zip(objs, self.expectedResults):
            self.assertEqual(obj.file, result)
            self.assertEqual(obj.image, result)

        # Export data to a file.
        with export_serializer.open_to_dump(result_path) as result_file:
            migration.export_data(result_file, export_serializer)

        with open(expected_path, 'rt') as expected_file:
            with open(result_path, 'rt') as result_file:
                self.assertEqual(
                        result_file.read().splitlines(),
                        expected_file.read().splitlines())

    def test_json_serializer(self):
        migration = FileMigration(FileModel)
        serializer = JsonSerializer()

        source_path = os.path.join(MIGRATIONS_DIR, 'file_source.json')
        expected_path = os.path.join(MIGRATIONS_DIR, 'file_result.json')
        result_path = os.path.join(self.temp_dir, 'file_result.json')

        # Import data from a string.
        with serializer.open_to_load(source_path) as source_file:
            migration.import_data(source_file.read(), serializer, DirectPlan)

        objs = list(FileModel.objects.all())
        self.assertEqual(len(objs), len(self.expectedResults))
        for obj, result in zip(objs, self.expectedResults):
            self.assertEqual(obj.file, result)
            self.assertEqual(obj.image, result)

        # Export data to a string.
        result = migration.export_data(serializer=serializer)

        with open(expected_path, 'rt') as expected_file:
            self.assertEqual(
                    result.splitlines(),
                    expected_file.read().splitlines())

        # Import data from a file.
        with serializer.open_to_load(source_path) as source_file:
            migration.import_data(source_file, serializer, ReplaceAllPlan)

        objs = list(FileModel.objects.all())
        self.assertEqual(len(objs), len(self.expectedResults))
        for obj, result in zip(objs, self.expectedResults):
            self.assertEqual(obj.file, result)
            self.assertEqual(obj.image, result)

        # Export data to a file.
        with serializer.open_to_dump(result_path) as result_file:
            migration.export_data(result_file, serializer)

        with open(expected_path, 'rt') as expected_file:
            with open(result_path, 'rt') as result_file:
                self.assertEqual(
                        result_file.read().splitlines(),
                        expected_file.read().splitlines())

    def test_tsv_serializer(self):
        migration = FileMigration(FileModel)
        import_serializer = TsvSerializer()
        export_serializer = TsvSerializer(quoting=csv.QUOTE_NONNUMERIC)

        source_path = os.path.join(MIGRATIONS_DIR, 'file_source.tsv')
        expected_path = os.path.join(MIGRATIONS_DIR, 'file_result.tsv')
        result_path = os.path.join(self.temp_dir, 'file_result.tsv')

        # Import data from a string.
        with import_serializer.open_to_load(source_path) as source_file:
            migration.import_data(source_file.read(), import_serializer, DirectPlan)

        objs = list(FileModel.objects.all())
        self.assertEqual(len(objs), len(self.expectedResults))
        for obj, result in zip(objs, self.expectedResults):
            self.assertEqual(obj.file, result)
            self.assertEqual(obj.image, result)

        # Export data to a string.
        result = migration.export_data(serializer=export_serializer)

        with import_serializer.open_to_load(expected_path) as expected_file:
            self.assertEqual(
                    result.splitlines(),
                    expected_file.read().splitlines())

        # Import data from a file.
        with import_serializer.open_to_load(source_path) as source_file:
            migration.import_data(source_file, import_serializer, ReplaceAllPlan)

        objs = list(FileModel.objects.all())
        self.assertEqual(len(objs), len(self.expectedResults))
        for obj, result in zip(objs, self.expectedResults):
            self.assertEqual(obj.file, result)
            self.assertEqual(obj.image, result)

        # Export data to a file.
        with export_serializer.open_to_dump(result_path) as result_file:
            migration.export_data(result_file, export_serializer)

        with open(expected_path, 'rt') as expected_file:
            with open(result_path, 'rt') as result_file:
                self.assertEqual(
                        result_file.read().splitlines(),
                        expected_file.read().splitlines())

    @expectedFailure
    def test_xls_serializer(self):
        migration = FileMigration(FileModel)
        import_serializer = CsvSerializer()
        export_serializer = CsvSerializer(quoting=csv.QUOTE_NONNUMERIC)
        binary_serializer = XlsSerializer()

        source_path = os.path.join(MIGRATIONS_DIR, 'file_source.csv')
        expected_path = os.path.join(MIGRATIONS_DIR, 'file_result.csv')
        result_path = os.path.join(self.temp_dir, 'file_result.csv')
        binary_path = os.path.join(self.temp_dir, 'file_result.xls')

        # Load initial data with a text serializer.
        with import_serializer.open_to_load(source_path) as source_file:

            with warnings.catch_warnings(record=True) as w:
                warnings.filterwarnings('ignore', 'naive file')
                migration.import_data(source_file, import_serializer, DirectPlan)

        objs = list(FileModel.objects.all())
        self.assertEqual(len(objs), len(self.expectedResults))
        for obj, result in zip(objs, self.expectedResults):
            self.assertEqual(obj.file, result)
            self.assertEqual(obj.image, result)

        # Export and import data with the binary serializer (replacing
        # previous data).
        binary_result = migration.export_data(serializer=binary_serializer)
        self.assertIsInstance(binary_result, six.binary_type)
        migration.import_data(binary_result, binary_serializer, ReplaceAllPlan)

        # Export resulting data with the text serializer and compare it
        # with the expected file.
        with export_serializer.open_to_dump(result_path) as result_file:
            migration.export_data(result_file, export_serializer)

        with open(expected_path, 'rt') as expected_file:
            with open(result_path, 'rt') as result_file:
                self.assertEqual(
                        result_file.read().splitlines(),
                        expected_file.read().splitlines())

        # Repeat the process using files instead of strings.
        with binary_serializer.open_to_dump(binary_path) as binary_file:
            migration.export_data(binary_file, binary_serializer)

        with binary_serializer.open_to_load(binary_path) as binary_file:
            migration.import_data(binary_file, binary_serializer, ReplaceAllPlan)

        with export_serializer.open_to_dump(result_path) as result_file:
            migration.export_data(result_file, export_serializer)

        with open(expected_path, 'rt') as expected_file:
            with open(result_path, 'rt') as result_file:
                self.assertEqual(
                        result_file.read().splitlines(),
                        expected_file.read().splitlines())

    def test_xlsx_serializer(self):
        migration = FileMigration(FileModel)
        import_serializer = CsvSerializer()
        export_serializer = CsvSerializer(quoting=csv.QUOTE_NONNUMERIC)
        binary_serializer = XlsxSerializer()

        source_path = os.path.join(MIGRATIONS_DIR, 'file_source.csv')
        expected_path = os.path.join(MIGRATIONS_DIR, 'file_result.csv')
        result_path = os.path.join(self.temp_dir, 'file_result.csv')
        binary_path = os.path.join(self.temp_dir, 'file_result.xlsx')

        # Load initial data with a text serializer.
        with import_serializer.open_to_load(source_path) as source_file:

            with warnings.catch_warnings(record=True) as w:
                warnings.filterwarnings('ignore', 'naive file')
                migration.import_data(source_file, import_serializer, DirectPlan)

        objs = list(FileModel.objects.all())
        self.assertEqual(len(objs), len(self.expectedResults))
        for obj, result in zip(objs, self.expectedResults):
            self.assertEqual(obj.file, result)
            self.assertEqual(obj.image, result)

        # Export and import data with the binary serializer (replacing
        # previous data).
        binary_result = migration.export_data(serializer=binary_serializer)
        self.assertIsInstance(binary_result, six.binary_type)
        migration.import_data(binary_result, binary_serializer, ReplaceAllPlan)

        # Export resulting data with the text serializer and compare it
        # with the expected file.
        with export_serializer.open_to_dump(result_path) as result_file:
            migration.export_data(result_file, export_serializer)

        with open(expected_path, 'rt') as expected_file:
            with open(result_path, 'rt') as result_file:
                self.assertEqual(
                        result_file.read().splitlines(),
                        expected_file.read().splitlines())

        # Repeat the process using files instead of strings.
        with binary_serializer.open_to_dump(binary_path) as binary_file:
            migration.export_data(binary_file, binary_serializer)

        with binary_serializer.open_to_load(binary_path) as binary_file:
            migration.import_data(binary_file, binary_serializer, ReplaceAllPlan)

        with export_serializer.open_to_dump(result_path) as result_file:
            migration.export_data(result_file, export_serializer)

        with open(expected_path, 'rt') as expected_file:
            with open(result_path, 'rt') as result_file:
                self.assertEqual(
                        result_file.read().splitlines(),
                        expected_file.read().splitlines())

    def test_yaml_serializer(self):
        migration = FileMigration(FileModel)
        serializer = YamlSerializer()

        source_path = os.path.join(MIGRATIONS_DIR, 'file_source.yaml')
        expected_path = os.path.join(MIGRATIONS_DIR, 'file_result.yaml')
        result_path = os.path.join(self.temp_dir, 'file_result.yaml')

        # Import data from a string.
        with serializer.open_to_load(source_path) as source_file:
            migration.import_data(source_file.read(), serializer, DirectPlan)

        objs = list(FileModel.objects.all())
        self.assertEqual(len(objs), len(self.expectedResults))
        for obj, result in zip(objs, self.expectedResults):
            self.assertEqual(obj.file, result)
            self.assertEqual(obj.image, result)

        # Export data to a string.
        result = migration.export_data(serializer=serializer)

        with open(expected_path, 'rt') as expected_file:
            self.assertEqual(
                    result.splitlines(),
                    expected_file.read().splitlines())

        # Import data from a file.
        with serializer.open_to_load(source_path) as source_file:
            migration.import_data(source_file, serializer, ReplaceAllPlan)

        objs = list(FileModel.objects.all())
        self.assertEqual(len(objs), len(self.expectedResults))
        for obj, result in zip(objs, self.expectedResults):
            self.assertEqual(obj.file, result)
            self.assertEqual(obj.image, result)

        # Export data to a file.
        with serializer.open_to_dump(result_path) as result_file:
            migration.export_data(result_file, serializer)

        with open(expected_path, 'rt') as expected_file:
            with open(result_path, 'rt') as result_file:
                self.assertEqual(
                        result_file.read().splitlines(),
                        expected_file.read().splitlines())


class NumericFieldsTests(TempDirMixin, test.TestCase):

    expectedResults = [
        (0, 0.0, Decimal("0")),
        (1, 0.1, Decimal("0.01")),
        (2, 0.2, Decimal("0.02")),
        (3, 0.3, Decimal("0.03")),
        (4, 0.4, Decimal("0.04")),
        (5, 0.5, Decimal("0.05")),
        (6, 0.6, Decimal("0.06")),
        (None, None, None),
        (None, None, None)
    ]
    maxDiff = None
    tempDirPrefix = 'test_data_migrations_'

    def test_data_migration(self):
        migration = NumericMigration(NumericModel)
        self.assertEqual(
            [repr(fld) for fld in migration.fields],
            ['<yepes.contrib.datamigrations.fields.IntegerField: integer>',
             '<yepes.contrib.datamigrations.fields.IntegerField: integer_as_string>',
             '<yepes.contrib.datamigrations.fields.FloatField: float>',
             '<yepes.contrib.datamigrations.fields.FloatField: float_as_string>',
             '<yepes.contrib.datamigrations.fields.NumberField: decimal>',
             '<yepes.contrib.datamigrations.fields.NumberField: decimal_as_string>'],
        )
        self.assertEqual(
            [repr(fld) for fld in migration.fields_to_import],
            ['<yepes.contrib.datamigrations.fields.IntegerField: integer>',
             '<yepes.contrib.datamigrations.fields.IntegerField: integer_as_string>',
             '<yepes.contrib.datamigrations.fields.FloatField: float>',
             '<yepes.contrib.datamigrations.fields.FloatField: float_as_string>',
             '<yepes.contrib.datamigrations.fields.NumberField: decimal>',
             '<yepes.contrib.datamigrations.fields.NumberField: decimal_as_string>'],
        )
        self.assertIsNone(migration.primary_key)
        self.assertIsNone(migration.natural_foreign_keys)
        self.assertTrue(migration.can_create)
        self.assertFalse(migration.can_update)
        self.assertFalse(migration.requires_model_instances)

    def test_csv_serializer(self):
        migration = NumericMigration(NumericModel)
        import_serializer = CsvSerializer()
        export_serializer = CsvSerializer(quoting=csv.QUOTE_NONNUMERIC)

        source_path = os.path.join(MIGRATIONS_DIR, 'numeric_source.csv')
        expected_path = os.path.join(MIGRATIONS_DIR, 'numeric_result.csv')
        result_path = os.path.join(self.temp_dir, 'numeric_result.csv')

        # Import data from a string.
        with import_serializer.open_to_load(source_path) as source_file:
            migration.import_data(source_file.read(), import_serializer, DirectPlan)

        objs = list(NumericModel.objects.all())
        self.assertEqual(len(objs), len(self.expectedResults))
        for obj, result in zip(objs, self.expectedResults):
            self.assertEqual(obj.integer, result[0])
            self.assertEqual(obj.integer_as_string, result[0])
            self.assertEqual(obj.float, result[1])
            self.assertEqual(obj.float_as_string, result[1])
            self.assertEqual(obj.decimal, result[2])
            self.assertEqual(obj.decimal_as_string, result[2])

        # Export data to a string.
        result = migration.export_data(serializer=export_serializer)

        with import_serializer.open_to_load(expected_path) as expected_file:
            self.assertEqual(
                    result.splitlines(),
                    expected_file.read().splitlines())

        # Import data from a file.
        with import_serializer.open_to_load(source_path) as source_file:
            migration.import_data(source_file, import_serializer, ReplaceAllPlan)

        objs = list(NumericModel.objects.all())
        self.assertEqual(len(objs), len(self.expectedResults))
        for obj, result in zip(objs, self.expectedResults):
            self.assertEqual(obj.integer, result[0])
            self.assertEqual(obj.integer_as_string, result[0])
            self.assertEqual(obj.float, result[1])
            self.assertEqual(obj.float_as_string, result[1])
            self.assertEqual(obj.decimal, result[2])
            self.assertEqual(obj.decimal_as_string, result[2])

        # Export data to a file.
        with export_serializer.open_to_dump(result_path) as result_file:
            migration.export_data(result_file, export_serializer)

        with open(expected_path, 'rt') as expected_file:
            with open(result_path, 'rt') as result_file:
                self.assertEqual(
                        result_file.read().splitlines(),
                        expected_file.read().splitlines())

    def test_json_serializer(self):
        migration = NumericMigration(NumericModel)
        serializer = JsonSerializer()

        source_path = os.path.join(MIGRATIONS_DIR, 'numeric_source.json')
        expected_path = os.path.join(MIGRATIONS_DIR, 'numeric_result.json')
        result_path = os.path.join(self.temp_dir, 'numeric_result.json')

        # Import data from a string.
        with serializer.open_to_load(source_path) as source_file:
            migration.import_data(source_file.read(), serializer, DirectPlan)

        objs = list(NumericModel.objects.all())
        self.assertEqual(len(objs), len(self.expectedResults))
        for obj, result in zip(objs, self.expectedResults):
            self.assertEqual(obj.integer, result[0])
            self.assertEqual(obj.integer_as_string, result[0])
            self.assertEqual(obj.float, result[1])
            self.assertEqual(obj.float_as_string, result[1])
            self.assertEqual(obj.decimal, result[2])
            self.assertEqual(obj.decimal_as_string, result[2])

        # Export data to a string.
        result = migration.export_data(serializer=serializer)

        with open(expected_path, 'rt') as expected_file:
            self.assertEqual(
                    result.splitlines(),
                    expected_file.read().splitlines())

        # Import data from a file.
        with serializer.open_to_load(source_path) as source_file:
            migration.import_data(source_file, serializer, ReplaceAllPlan)

        objs = list(NumericModel.objects.all())
        self.assertEqual(len(objs), len(self.expectedResults))
        for obj, result in zip(objs, self.expectedResults):
            self.assertEqual(obj.integer, result[0])
            self.assertEqual(obj.integer_as_string, result[0])
            self.assertEqual(obj.float, result[1])
            self.assertEqual(obj.float_as_string, result[1])
            self.assertEqual(obj.decimal, result[2])
            self.assertEqual(obj.decimal_as_string, result[2])

        # Export data to a file.
        with serializer.open_to_dump(result_path) as result_file:
            migration.export_data(result_file, serializer)

        with open(expected_path, 'rt') as expected_file:
            with open(result_path, 'rt') as result_file:
                self.assertEqual(
                        result_file.read().splitlines(),
                        expected_file.read().splitlines())

    def test_tsv_serializer(self):
        migration = NumericMigration(NumericModel)
        import_serializer = TsvSerializer()
        export_serializer = TsvSerializer(quoting=csv.QUOTE_NONNUMERIC)

        source_path = os.path.join(MIGRATIONS_DIR, 'numeric_source.tsv')
        expected_path = os.path.join(MIGRATIONS_DIR, 'numeric_result.tsv')
        result_path = os.path.join(self.temp_dir, 'numeric_result.tsv')

        # Import data from a string.
        with import_serializer.open_to_load(source_path) as source_file:
            migration.import_data(source_file.read(), import_serializer, DirectPlan)

        objs = list(NumericModel.objects.all())
        self.assertEqual(len(objs), len(self.expectedResults))
        for obj, result in zip(objs, self.expectedResults):
            self.assertEqual(obj.integer, result[0])
            self.assertEqual(obj.integer_as_string, result[0])
            self.assertEqual(obj.float, result[1])
            self.assertEqual(obj.float_as_string, result[1])
            self.assertEqual(obj.decimal, result[2])
            self.assertEqual(obj.decimal_as_string, result[2])

        # Export data to a string.
        result = migration.export_data(serializer=export_serializer)

        with import_serializer.open_to_load(expected_path) as expected_file:
            self.assertEqual(
                    result.splitlines(),
                    expected_file.read().splitlines())

        # Import data from a file.
        with import_serializer.open_to_load(source_path) as source_file:
            migration.import_data(source_file, import_serializer, ReplaceAllPlan)

        objs = list(NumericModel.objects.all())
        self.assertEqual(len(objs), len(self.expectedResults))
        for obj, result in zip(objs, self.expectedResults):
            self.assertEqual(obj.integer, result[0])
            self.assertEqual(obj.integer_as_string, result[0])
            self.assertEqual(obj.float, result[1])
            self.assertEqual(obj.float_as_string, result[1])
            self.assertEqual(obj.decimal, result[2])
            self.assertEqual(obj.decimal_as_string, result[2])

        # Export data to a file.
        with export_serializer.open_to_dump(result_path) as result_file:
            migration.export_data(result_file, export_serializer)

        with open(expected_path, 'rt') as expected_file:
            with open(result_path, 'rt') as result_file:
                self.assertEqual(
                        result_file.read().splitlines(),
                        expected_file.read().splitlines())

    def test_xls_serializer(self):
        migration = NumericMigration(NumericModel)
        import_serializer = CsvSerializer()
        export_serializer = CsvSerializer(quoting=csv.QUOTE_NONNUMERIC)
        binary_serializer = XlsSerializer()

        source_path = os.path.join(MIGRATIONS_DIR, 'numeric_source.csv')
        expected_path = os.path.join(MIGRATIONS_DIR, 'numeric_result.csv')
        result_path = os.path.join(self.temp_dir, 'numeric_result.csv')
        binary_path = os.path.join(self.temp_dir, 'numeric_result.xls')

        # Load initial data with a text serializer.
        with import_serializer.open_to_load(source_path) as source_file:
            migration.import_data(source_file, import_serializer, DirectPlan)

        objs = list(NumericModel.objects.all())
        self.assertEqual(len(objs), len(self.expectedResults))
        for obj, result in zip(objs, self.expectedResults):
            self.assertEqual(obj.integer, result[0])
            self.assertEqual(obj.integer_as_string, result[0])
            self.assertEqual(obj.float, result[1])
            self.assertEqual(obj.float_as_string, result[1])
            self.assertEqual(obj.decimal, result[2])
            self.assertEqual(obj.decimal_as_string, result[2])

        # Export and import data with the binary serializer (replacing
        # previous data).
        binary_result = migration.export_data(serializer=binary_serializer)
        self.assertIsInstance(binary_result, six.binary_type)
        migration.import_data(binary_result, binary_serializer, ReplaceAllPlan)

        # Export resulting data with the text serializer and compare it
        # with the expected file.
        with export_serializer.open_to_dump(result_path) as result_file:
            migration.export_data(result_file, export_serializer)

        with open(expected_path, 'rt') as expected_file:
            with open(result_path, 'rt') as result_file:
                self.assertEqual(
                        result_file.read().splitlines(),
                        expected_file.read().splitlines())

        # Repeat the process using files instead of strings.
        with binary_serializer.open_to_dump(binary_path) as binary_file:
            migration.export_data(binary_file, binary_serializer)

        with binary_serializer.open_to_load(binary_path) as binary_file:
            migration.import_data(binary_file, binary_serializer, ReplaceAllPlan)

        with export_serializer.open_to_dump(result_path) as result_file:
            migration.export_data(result_file, export_serializer)

        with open(expected_path, 'rt') as expected_file:
            with open(result_path, 'rt') as result_file:
                self.assertEqual(
                        result_file.read().splitlines(),
                        expected_file.read().splitlines())

    def test_xlsx_serializer(self):
        migration = NumericMigration(NumericModel)
        import_serializer = CsvSerializer()
        export_serializer = CsvSerializer(quoting=csv.QUOTE_NONNUMERIC)
        binary_serializer = XlsxSerializer()

        source_path = os.path.join(MIGRATIONS_DIR, 'numeric_source.csv')
        expected_path = os.path.join(MIGRATIONS_DIR, 'numeric_result.csv')
        result_path = os.path.join(self.temp_dir, 'numeric_result.csv')
        binary_path = os.path.join(self.temp_dir, 'numeric_result.xlsx')

        # Load initial data with a text serializer.
        with import_serializer.open_to_load(source_path) as source_file:
            migration.import_data(source_file, import_serializer, DirectPlan)

        objs = list(NumericModel.objects.all())
        self.assertEqual(len(objs), len(self.expectedResults))
        for obj, result in zip(objs, self.expectedResults):
            self.assertEqual(obj.integer, result[0])
            self.assertEqual(obj.integer_as_string, result[0])
            self.assertEqual(obj.float, result[1])
            self.assertEqual(obj.float_as_string, result[1])
            self.assertEqual(obj.decimal, result[2])
            self.assertEqual(obj.decimal_as_string, result[2])

        # Export and import data with the binary serializer (replacing
        # previous data).
        binary_result = migration.export_data(serializer=binary_serializer)
        self.assertIsInstance(binary_result, six.binary_type)
        migration.import_data(binary_result, binary_serializer, ReplaceAllPlan)

        # Export resulting data with the text serializer and compare it
        # with the expected file.
        with export_serializer.open_to_dump(result_path) as result_file:
            migration.export_data(result_file, export_serializer)

        with open(expected_path, 'rt') as expected_file:
            with open(result_path, 'rt') as result_file:
                self.assertEqual(
                        result_file.read().splitlines(),
                        expected_file.read().splitlines())

        # Repeat the process using files instead of strings.
        with binary_serializer.open_to_dump(binary_path) as binary_file:
            migration.export_data(binary_file, binary_serializer)

        with binary_serializer.open_to_load(binary_path) as binary_file:
            migration.import_data(binary_file, binary_serializer, ReplaceAllPlan)

        with export_serializer.open_to_dump(result_path) as result_file:
            migration.export_data(result_file, export_serializer)

        with open(expected_path, 'rt') as expected_file:
            with open(result_path, 'rt') as result_file:
                self.assertEqual(
                        result_file.read().splitlines(),
                        expected_file.read().splitlines())

    def test_yaml_serializer(self):
        migration = NumericMigration(NumericModel)
        serializer = YamlSerializer()

        source_path = os.path.join(MIGRATIONS_DIR, 'numeric_source.yaml')
        expected_path = os.path.join(MIGRATIONS_DIR, 'numeric_result.yaml')
        result_path = os.path.join(self.temp_dir, 'numeric_result.yaml')

        # Import data from a string.
        with serializer.open_to_load(source_path) as source_file:
            migration.import_data(source_file.read(), serializer, DirectPlan)

        objs = list(NumericModel.objects.all())
        self.assertEqual(len(objs), len(self.expectedResults))
        for obj, result in zip(objs, self.expectedResults):
            self.assertEqual(obj.integer, result[0])
            self.assertEqual(obj.integer_as_string, result[0])
            self.assertEqual(obj.float, result[1])
            self.assertEqual(obj.float_as_string, result[1])
            self.assertEqual(obj.decimal, result[2])
            self.assertEqual(obj.decimal_as_string, result[2])

        # Export data to a string.
        result = migration.export_data(serializer=serializer)

        with open(expected_path, 'rt') as expected_file:
            self.assertEqual(
                    result.splitlines(),
                    expected_file.read().splitlines())

        # Import data from a file.
        with serializer.open_to_load(source_path) as source_file:
            migration.import_data(source_file, serializer, ReplaceAllPlan)

        objs = list(NumericModel.objects.all())
        self.assertEqual(len(objs), len(self.expectedResults))
        for obj, result in zip(objs, self.expectedResults):
            self.assertEqual(obj.integer, result[0])
            self.assertEqual(obj.integer_as_string, result[0])
            self.assertEqual(obj.float, result[1])
            self.assertEqual(obj.float_as_string, result[1])
            self.assertEqual(obj.decimal, result[2])
            self.assertEqual(obj.decimal_as_string, result[2])

        # Export data to a file.
        with serializer.open_to_dump(result_path) as result_file:
            migration.export_data(result_file, serializer)

        with open(expected_path, 'rt') as expected_file:
            with open(result_path, 'rt') as result_file:
                self.assertEqual(
                        result_file.read().splitlines(),
                        expected_file.read().splitlines())


class TextFieldsTests(TempDirMixin, test.TestCase):

    expectedResults = [
        '0',
        '1234',
        'a',
        'abcd',
        'abcd efgh',
        'abcd efgh\nijkl',
        '"Fix, Schwyz!" quäkt Jürgen blöd vom Paß.',
        'Fabio me exige, sin tapujos, que añada cerveza al whisky.',
        "Le cœur déçu mais l'âme plutôt naïve, Louÿs rêva de crapaüter en canoë au delà des îles, près du mälströn où brûlent les novæ.",
        'Luís argüía à Júlia que «brações, fé, chá, óxido, pôr, zângão» eram palavras do português.',
        'Съешь еще этих мягких французских булок, да выпей чаю.',
        '',
        None,
    ]
    maxDiff = None
    tempDirPrefix = 'test_data_migrations_'

    def test_data_migration(self):
        migration = TextMigration(TextModel)
        self.assertEqual(
            [repr(fld) for fld in migration.fields],
            ['<yepes.contrib.datamigrations.fields.TextField: char>',
             '<yepes.contrib.datamigrations.fields.TextField: text>'],
        )
        self.assertEqual(
            [repr(fld) for fld in migration.fields_to_import],
            ['<yepes.contrib.datamigrations.fields.TextField: char>',
             '<yepes.contrib.datamigrations.fields.TextField: text>'],
        )
        self.assertIsNone(migration.primary_key)
        self.assertIsNone(migration.natural_foreign_keys)
        self.assertTrue(migration.can_create)
        self.assertFalse(migration.can_update)
        self.assertFalse(migration.requires_model_instances)

    def test_csv_serializer(self):
        migration = TextMigration(TextModel)
        import_serializer = CsvSerializer()
        export_serializer = CsvSerializer(quoting=csv.QUOTE_NONNUMERIC)

        source_path = os.path.join(MIGRATIONS_DIR, 'text_source.csv')
        expected_path = os.path.join(MIGRATIONS_DIR, 'text_result.csv')
        result_path = os.path.join(self.temp_dir, 'text_result.csv')

        # Import data from a string.
        with import_serializer.open_to_load(source_path) as source_file:
            migration.import_data(source_file.read(), import_serializer, DirectPlan)

        objs = list(TextModel.objects.all())
        self.assertEqual(len(objs), len(self.expectedResults))
        for obj, result in zip(objs, self.expectedResults):
            self.assertEqual(obj.char, result)
            self.assertEqual(obj.text, result)

        # Export data to a string.
        result = migration.export_data(serializer=export_serializer)

        with import_serializer.open_to_load(expected_path) as expected_file:
            self.assertEqual(
                    result.splitlines(),
                    expected_file.read().splitlines())

        # Import data from a file.
        with import_serializer.open_to_load(source_path) as source_file:
            migration.import_data(source_file, import_serializer, ReplaceAllPlan)

        objs = list(TextModel.objects.all())
        self.assertEqual(len(objs), len(self.expectedResults))
        for obj, result in zip(objs, self.expectedResults):
            self.assertEqual(obj.char, result)
            self.assertEqual(obj.text, result)

        # Export data to a file.
        with export_serializer.open_to_dump(result_path) as result_file:
            migration.export_data(result_file, export_serializer)

        with open(expected_path, 'rt') as expected_file:
            with open(result_path, 'rt') as result_file:
                self.assertEqual(
                        result_file.read().splitlines(),
                        expected_file.read().splitlines())

    def test_json_serializer(self):
        migration = TextMigration(TextModel)
        serializer = JsonSerializer()

        source_path = os.path.join(MIGRATIONS_DIR, 'text_source.json')
        expected_path = os.path.join(MIGRATIONS_DIR, 'text_result.json')
        result_path = os.path.join(self.temp_dir, 'text_result.json')

        # Import data from a string.
        with serializer.open_to_load(source_path) as source_file:
            migration.import_data(source_file.read(), serializer, DirectPlan)

        objs = list(TextModel.objects.all())
        self.assertEqual(len(objs), len(self.expectedResults))
        for obj, result in zip(objs, self.expectedResults):
            self.assertEqual(obj.char, result)
            self.assertEqual(obj.text, result)

        # Export data to a string.
        result = migration.export_data(serializer=serializer)

        with open(expected_path, 'rt') as expected_file:
            self.assertEqual(
                    result.splitlines(),
                    expected_file.read().splitlines())

        # Import data from a file.
        with serializer.open_to_load(source_path) as source_file:
            migration.import_data(source_file, serializer, ReplaceAllPlan)

        objs = list(TextModel.objects.all())
        self.assertEqual(len(objs), len(self.expectedResults))
        for obj, result in zip(objs, self.expectedResults):
            self.assertEqual(obj.char, result)
            self.assertEqual(obj.text, result)

        # Export data to a file.
        with serializer.open_to_dump(result_path) as result_file:
            migration.export_data(result_file, serializer)

        with open(expected_path, 'rt') as expected_file:
            with open(result_path, 'rt') as result_file:
                self.assertEqual(
                        result_file.read().splitlines(),
                        expected_file.read().splitlines())

    def test_tsv_serializer(self):
        migration = TextMigration(TextModel)
        import_serializer = TsvSerializer()
        export_serializer = TsvSerializer(quoting=csv.QUOTE_NONNUMERIC)

        source_path = os.path.join(MIGRATIONS_DIR, 'text_source.tsv')
        expected_path = os.path.join(MIGRATIONS_DIR, 'text_result.tsv')
        result_path = os.path.join(self.temp_dir, 'text_result.tsv')

        # Import data from a string.
        with import_serializer.open_to_load(source_path) as source_file:
            migration.import_data(source_file.read(), import_serializer, DirectPlan)

        objs = list(TextModel.objects.all())
        self.assertEqual(len(objs), len(self.expectedResults))
        for obj, result in zip(objs, self.expectedResults):
            self.assertEqual(obj.char, result)
            self.assertEqual(obj.text, result)

        # Export data to a string.
        result = migration.export_data(serializer=export_serializer)

        with import_serializer.open_to_load(expected_path) as expected_file:
            self.assertEqual(
                    result.splitlines(),
                    expected_file.read().splitlines())

        # Import data from a file.
        with import_serializer.open_to_load(source_path) as source_file:
            migration.import_data(source_file, import_serializer, ReplaceAllPlan)

        objs = list(TextModel.objects.all())
        self.assertEqual(len(objs), len(self.expectedResults))
        for obj, result in zip(objs, self.expectedResults):
            self.assertEqual(obj.char, result)
            self.assertEqual(obj.text, result)

        # Export data to a file.
        with export_serializer.open_to_dump(result_path) as result_file:
            migration.export_data(result_file, export_serializer)

        with open(expected_path, 'rt') as expected_file:
            with open(result_path, 'rt') as result_file:
                self.assertEqual(
                        result_file.read().splitlines(),
                        expected_file.read().splitlines())

    def test_xls_serializer(self):
        migration = TextMigration(TextModel)
        import_serializer = CsvSerializer()
        export_serializer = CsvSerializer(quoting=csv.QUOTE_NONNUMERIC)
        binary_serializer = XlsSerializer()

        source_path = os.path.join(MIGRATIONS_DIR, 'text_source.csv')
        expected_path = os.path.join(MIGRATIONS_DIR, 'text_result.csv')
        result_path = os.path.join(self.temp_dir, 'text_result.csv')
        binary_path = os.path.join(self.temp_dir, 'text_result.xls')

        # Load initial data with a text serializer.
        with import_serializer.open_to_load(source_path) as source_file:
            migration.import_data(source_file, import_serializer, DirectPlan)

        objs = list(TextModel.objects.all())
        self.assertEqual(len(objs), len(self.expectedResults))
        for obj, result in zip(objs, self.expectedResults):
            self.assertEqual(obj.char, result)
            self.assertEqual(obj.text, result)

        # Export and import data with the binary serializer (replacing
        # previous data).
        binary_result = migration.export_data(serializer=binary_serializer)
        self.assertIsInstance(binary_result, six.binary_type)
        migration.import_data(binary_result, binary_serializer, ReplaceAllPlan)

        # Export resulting data with the text serializer and compare it
        # with the expected file.
        with export_serializer.open_to_dump(result_path) as result_file:
            migration.export_data(result_file, export_serializer)

        with open(expected_path, 'rt') as expected_file:
            with open(result_path, 'rt') as result_file:
                self.assertEqual(
                        result_file.read().splitlines(),
                        expected_file.read().splitlines())

        # Repeat the process using files instead of strings.
        with binary_serializer.open_to_dump(binary_path) as binary_file:
            migration.export_data(binary_file, binary_serializer)

        with binary_serializer.open_to_load(binary_path) as binary_file:
            migration.import_data(binary_file, binary_serializer, ReplaceAllPlan)

        with export_serializer.open_to_dump(result_path) as result_file:
            migration.export_data(result_file, export_serializer)

        with open(expected_path, 'rt') as expected_file:
            with open(result_path, 'rt') as result_file:
                self.assertEqual(
                        result_file.read().splitlines(),
                        expected_file.read().splitlines())

    @expectedFailure
    def test_xlsx_serializer(self):
        migration = TextMigration(TextModel)
        import_serializer = CsvSerializer()
        export_serializer = CsvSerializer(quoting=csv.QUOTE_NONNUMERIC)
        binary_serializer = XlsxSerializer()

        source_path = os.path.join(MIGRATIONS_DIR, 'text_source.csv')
        expected_path = os.path.join(MIGRATIONS_DIR, 'text_result.csv')
        result_path = os.path.join(self.temp_dir, 'text_result.csv')
        binary_path = os.path.join(self.temp_dir, 'text_result.xlsx')

        # Load initial data with a text serializer.
        with import_serializer.open_to_load(source_path) as source_file:
            migration.import_data(source_file, import_serializer, DirectPlan)

        objs = list(TextModel.objects.all())
        self.assertEqual(len(objs), len(self.expectedResults))
        for obj, result in zip(objs, self.expectedResults):
            self.assertEqual(obj.char, result)
            self.assertEqual(obj.text, result)

        # Export and import data with the binary serializer (replacing
        # previous data).
        binary_result = migration.export_data(serializer=binary_serializer)
        self.assertIsInstance(binary_result, six.binary_type)
        migration.import_data(binary_result, binary_serializer, ReplaceAllPlan)

        # Export resulting data with the text serializer and compare it
        # with the expected file.
        with export_serializer.open_to_dump(result_path) as result_file:
            migration.export_data(result_file, export_serializer)

        with open(expected_path, 'rt') as expected_file:
            with open(result_path, 'rt') as result_file:
                self.assertEqual(
                        result_file.read().splitlines(),
                        expected_file.read().splitlines())

        # Repeat the process using files instead of strings.
        with binary_serializer.open_to_dump(binary_path) as binary_file:
            migration.export_data(binary_file, binary_serializer)

        with binary_serializer.open_to_load(binary_path) as binary_file:
            migration.import_data(binary_file, binary_serializer, ReplaceAllPlan)

        with export_serializer.open_to_dump(result_path) as result_file:
            migration.export_data(result_file, export_serializer)

        with open(expected_path, 'rt') as expected_file:
            with open(result_path, 'rt') as result_file:
                self.assertEqual(
                        result_file.read().splitlines(),
                        expected_file.read().splitlines())

    def test_yaml_serializer(self):
        migration = TextMigration(TextModel)
        serializer = YamlSerializer()

        source_path = os.path.join(MIGRATIONS_DIR, 'text_source.yaml')
        expected_path = os.path.join(MIGRATIONS_DIR, 'text_result.yaml')
        result_path = os.path.join(self.temp_dir, 'text_result.yaml')

        # Import data from a string.
        with serializer.open_to_load(source_path) as source_file:
            migration.import_data(source_file.read(), serializer, DirectPlan)

        objs = list(TextModel.objects.all())
        self.assertEqual(len(objs), len(self.expectedResults))
        for obj, result in zip(objs, self.expectedResults):
            self.assertEqual(obj.char, result)
            self.assertEqual(obj.text, result)

        # Export data to a string.
        result = migration.export_data(serializer=serializer)

        with open(expected_path, 'rt') as expected_file:
            self.assertEqual(
                    result.splitlines(),
                    expected_file.read().splitlines())

        # Import data from a file.
        with serializer.open_to_load(source_path) as source_file:
            migration.import_data(source_file, serializer, ReplaceAllPlan)

        objs = list(TextModel.objects.all())
        self.assertEqual(len(objs), len(self.expectedResults))
        for obj, result in zip(objs, self.expectedResults):
            self.assertEqual(obj.char, result)
            self.assertEqual(obj.text, result)

        # Export data to a file.
        with serializer.open_to_dump(result_path) as result_file:
            migration.export_data(result_file, serializer)

        with open(expected_path, 'rt') as expected_file:
            with open(result_path, 'rt') as result_file:
                self.assertEqual(
                        result_file.read().splitlines(),
                        expected_file.read().splitlines())

