# -*- coding:utf-8 -*-

from __future__ import unicode_literals

import collections
import csv
from datetime import date, datetime, time
from decimal import Decimal
from itertools import chain
import os
import shutil
import tempfile
import warnings

from django import test
from django.test.utils import override_settings
from django.utils import six
from django.utils._os import upath
from django.utils.six.moves import zip
from django.utils.timezone import utc as UTC

from yepes.data_migrations import (
    DataMigration,
    importation_plans,
    QuerySetExportation,
    serializers,
)
from yepes.data_migrations.importation_plans.direct import DirectPlan
from yepes.data_migrations.serializers.csv import CsvSerializer
from yepes.data_migrations.serializers.json import JsonSerializer
from yepes.data_migrations.serializers.tsv import TsvSerializer
from yepes.data_migrations.serializers.yaml import YamlSerializer

from .data_migrations import (
    AlphabetMigration,
    AuthorMigration,
    BlogMigration,
    BlogCategoryMigration,
    BooleanMigration,
    DateTimeMigration,
    DateTimeEdgeMigration,
    NumericMigration,
    TextMigration,
)
from .models import (
    AlphabetModel,
    AuthorModel,
    BlogModel,
    BlogCategoryModel,
    BooleanModel,
    DateTimeModel,
    NumericModel,
    PostModel,
    TextModel,
)

MODULE_DIR = os.path.abspath(os.path.dirname(upath(__file__)))
FIXTURES_DIR = os.path.join(MODULE_DIR, 'data_migrations')


class TempDirMixin(object):

    @classmethod
    def setUpClass(cls):
        super(TempDirMixin, cls).setUpClass()
        cls.temp_dir = tempfile.mkdtemp(prefix='test_data_migrations_')

    @classmethod
    def tearDownClass(cls):
        super(TempDirMixin, cls).tearDownClass()
        try:
            shutil.rmtree(six.text_type(cls.temp_dir))
        except OSError:
            self.stream.write('Failed to remove temp directory: {0}'.format(cls.temp_dir))


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

    def test_data_migration(self):
        migration = BooleanMigration(BooleanModel)
        self.assertEqual(
            [repr(fld) for fld in migration.fields],
            ['<yepes.data_migrations.fields.BooleanField: boolean>',
             '<yepes.data_migrations.fields.BooleanField: boolean_as_string>',
             '<yepes.data_migrations.fields.BooleanField: null_boolean>',
             '<yepes.data_migrations.fields.BooleanField: null_boolean_as_string>'],
        )
        self.assertEqual(
            [repr(fld) for fld in migration.fields_to_import],
            ['<yepes.data_migrations.fields.BooleanField: boolean>',
             '<yepes.data_migrations.fields.BooleanField: boolean_as_string>',
             '<yepes.data_migrations.fields.BooleanField: null_boolean>',
             '<yepes.data_migrations.fields.BooleanField: null_boolean_as_string>'],
        )
        self.assertIsNone(migration.primary_key)
        self.assertIsNone(migration.natural_foreign_keys)
        self.assertTrue(migration.can_create)
        self.assertFalse(migration.can_update)
        self.assertFalse(migration.requires_model_instances)

    def test_csv_serializer(self):
        migration = BooleanMigration(BooleanModel)
        import_serializer = CsvSerializer
        export_serializer = CsvSerializer(quoting=csv.QUOTE_NONNUMERIC)

        source_path = os.path.join(FIXTURES_DIR, 'boolean_source.csv')
        expected_path = os.path.join(FIXTURES_DIR, 'boolean_result.csv')
        result_path = os.path.join(self.temp_dir, 'boolean_result.csv')

        with open(source_path, 'rb') as source_file:

            migration.import_data(source_file.read(), import_serializer, DirectPlan)

            objs = list(BooleanModel.objects.all())
            self.assertEqual(len(objs), len(self.expectedResults))
            for obj, result in zip(objs, self.expectedResults):
                self.assertEqual(obj.boolean, result[0])
                self.assertEqual(obj.boolean_as_string, result[0])
                self.assertEqual(obj.null_boolean, result[1])
                self.assertEqual(obj.null_boolean_as_string, result[1])

        with open(expected_path, 'rb') as expected_file:
            with open(result_path, 'wb+') as result_file:

                result = migration.export_data(serializer=export_serializer)
                self.assertEqual(
                        result.splitlines(),
                        expected_file.read().splitlines())

        BooleanModel.objects.all().delete()
        with open(source_path, 'rb') as source_file:

            migration.import_data(source_file, import_serializer, DirectPlan)

            objs = list(BooleanModel.objects.all())
            self.assertEqual(len(objs), len(self.expectedResults))
            for obj, result in zip(objs, self.expectedResults):
                self.assertEqual(obj.boolean, result[0])
                self.assertEqual(obj.boolean_as_string, result[0])
                self.assertEqual(obj.null_boolean, result[1])
                self.assertEqual(obj.null_boolean_as_string, result[1])

        with open(expected_path, 'rb') as expected_file:
            with open(result_path, 'wb+') as result_file:

                migration.export_data(result_file, export_serializer)
                result_file.seek(0)
                self.assertEqual(
                        result_file.read().splitlines(),
                        expected_file.read().splitlines())

    def test_json_serializer(self):
        migration = BooleanMigration(BooleanModel)
        serializer = JsonSerializer

        source_path = os.path.join(FIXTURES_DIR, 'boolean_source.json')
        expected_path = os.path.join(FIXTURES_DIR, 'boolean_result.json')
        result_path = os.path.join(self.temp_dir, 'boolean_result.json')

        with open(source_path, 'rb') as source_file:

            migration.import_data(source_file.read(), serializer, DirectPlan)

            objs = list(BooleanModel.objects.all())
            self.assertEqual(len(objs), len(self.expectedResults))
            for obj, result in zip(objs, self.expectedResults):
                self.assertEqual(obj.boolean, result[0])
                self.assertEqual(obj.boolean_as_string, result[0])
                self.assertEqual(obj.null_boolean, result[1])
                self.assertEqual(obj.null_boolean_as_string, result[1])

        with open(expected_path, 'rb') as expected_file:
            with open(result_path, 'wb+') as result_file:

                result = migration.export_data(serializer=serializer)
                self.assertEqual(
                        result.splitlines(),
                        expected_file.read().splitlines())

        BooleanModel.objects.all().delete()
        with open(source_path, 'rb') as source_file:

            migration.import_data(source_file, serializer, DirectPlan)

            objs = list(BooleanModel.objects.all())
            self.assertEqual(len(objs), len(self.expectedResults))
            for obj, result in zip(objs, self.expectedResults):
                self.assertEqual(obj.boolean, result[0])
                self.assertEqual(obj.boolean_as_string, result[0])
                self.assertEqual(obj.null_boolean, result[1])
                self.assertEqual(obj.null_boolean_as_string, result[1])

        with open(expected_path, 'rb') as expected_file:
            with open(result_path, 'wb+') as result_file:

                migration.export_data(result_file, serializer)
                result_file.seek(0)
                self.assertEqual(
                        result_file.read().splitlines(),
                        expected_file.read().splitlines())

    def test_tsv_serializer(self):
        migration = BooleanMigration(BooleanModel)
        import_serializer = TsvSerializer
        export_serializer = TsvSerializer(quoting=csv.QUOTE_NONNUMERIC)

        source_path = os.path.join(FIXTURES_DIR, 'boolean_source.tsv')
        expected_path = os.path.join(FIXTURES_DIR, 'boolean_result.tsv')
        result_path = os.path.join(self.temp_dir, 'boolean_result.tsv')

        with open(source_path, 'rb') as source_file:

            migration.import_data(source_file.read(), import_serializer, DirectPlan)

            objs = list(BooleanModel.objects.all())
            self.assertEqual(len(objs), len(self.expectedResults))
            for obj, result in zip(objs, self.expectedResults):
                self.assertEqual(obj.boolean, result[0])
                self.assertEqual(obj.boolean_as_string, result[0])
                self.assertEqual(obj.null_boolean, result[1])
                self.assertEqual(obj.null_boolean_as_string, result[1])

        with open(expected_path, 'rb') as expected_file:
            with open(result_path, 'wb+') as result_file:

                result = migration.export_data(serializer=export_serializer)
                self.assertEqual(
                        result.splitlines(),
                        expected_file.read().splitlines())

        BooleanModel.objects.all().delete()
        with open(source_path, 'rb') as source_file:

            migration.import_data(source_file, import_serializer, DirectPlan)

            objs = list(BooleanModel.objects.all())
            self.assertEqual(len(objs), len(self.expectedResults))
            for obj, result in zip(objs, self.expectedResults):
                self.assertEqual(obj.boolean, result[0])
                self.assertEqual(obj.boolean_as_string, result[0])
                self.assertEqual(obj.null_boolean, result[1])
                self.assertEqual(obj.null_boolean_as_string, result[1])

        with open(expected_path, 'rb') as expected_file:
            with open(result_path, 'wb+') as result_file:

                migration.export_data(result_file, export_serializer)
                result_file.seek(0)
                self.assertEqual(
                        result_file.read().splitlines(),
                        expected_file.read().splitlines())

    def test_yaml_serializer(self):
        migration = BooleanMigration(BooleanModel)
        serializer = YamlSerializer

        source_path = os.path.join(FIXTURES_DIR, 'boolean_source.yaml')
        expected_path = os.path.join(FIXTURES_DIR, 'boolean_result.yaml')
        result_path = os.path.join(self.temp_dir, 'boolean_result.yaml')

        with open(source_path, 'rb') as source_file:

            migration.import_data(source_file.read(), serializer, DirectPlan)

            objs = list(BooleanModel.objects.all())
            self.assertEqual(len(objs), len(self.expectedResults))
            for obj, result in zip(objs, self.expectedResults):
                self.assertEqual(obj.boolean, result[0])
                self.assertEqual(obj.boolean_as_string, result[0])
                self.assertEqual(obj.null_boolean, result[1])
                self.assertEqual(obj.null_boolean_as_string, result[1])

        with open(expected_path, 'rb') as expected_file:
            with open(result_path, 'wb+') as result_file:

                result = migration.export_data(serializer=serializer)
                self.assertEqual(
                        result.splitlines(),
                        expected_file.read().splitlines())

        BooleanModel.objects.all().delete()
        with open(source_path, 'rb') as source_file:

            migration.import_data(source_file, serializer, DirectPlan)

            objs = list(BooleanModel.objects.all())
            self.assertEqual(len(objs), len(self.expectedResults))
            for obj, result in zip(objs, self.expectedResults):
                self.assertEqual(obj.boolean, result[0])
                self.assertEqual(obj.boolean_as_string, result[0])
                self.assertEqual(obj.null_boolean, result[1])
                self.assertEqual(obj.null_boolean_as_string, result[1])

        with open(expected_path, 'rb') as expected_file:
            with open(result_path, 'wb+') as result_file:

                migration.export_data(result_file, serializer)
                result_file.seek(0)
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

    def test_data_migrations(self):
        migration = DateTimeMigration(DateTimeModel)
        self.assertEqual(
            [repr(fld) for fld in migration.fields],
            ['<yepes.data_migrations.fields.DateField: date>',
             '<yepes.data_migrations.fields.YearField: date__year>',
             '<yepes.data_migrations.fields.MonthField: date__month>',
             '<yepes.data_migrations.fields.DayField: date__day>',
             '<yepes.data_migrations.fields.DateTimeField: datetime>',
             '<yepes.data_migrations.fields.YearField: datetime__year>',
             '<yepes.data_migrations.fields.MonthField: datetime__month>',
             '<yepes.data_migrations.fields.DayField: datetime__day>',
             '<yepes.data_migrations.fields.HourField: datetime__hour>',
             '<yepes.data_migrations.fields.MinuteField: datetime__minute>',
             '<yepes.data_migrations.fields.SecondField: datetime__second>',
             '<yepes.data_migrations.fields.MicrosecondField: datetime__microsecond>',
             '<yepes.data_migrations.fields.TimeZoneField: datetime__tzinfo>',
             '<yepes.data_migrations.fields.TimeField: time>',
             '<yepes.data_migrations.fields.HourField: time__hour>',
             '<yepes.data_migrations.fields.MinuteField: time__minute>',
             '<yepes.data_migrations.fields.SecondField: time__second>',
             '<yepes.data_migrations.fields.MicrosecondField: time__microsecond>',
             '<yepes.data_migrations.fields.TimeZoneField: time__tzinfo>'],
        )
        self.assertEqual(
            [repr(fld) for fld in migration.fields_to_import],
            ['<yepes.data_migrations.fields.DateField: date>',
             '<yepes.data_migrations.fields.DateTimeField: datetime>',
             '<yepes.data_migrations.fields.TimeField: time>'],
        )
        self.assertIsNone(migration.primary_key)
        self.assertIsNone(migration.natural_foreign_keys)
        self.assertTrue(migration.can_create)
        self.assertFalse(migration.can_update)
        self.assertTrue(migration.requires_model_instances)

        migration = DateTimeEdgeMigration(DateTimeModel)
        self.assertEqual(
            [repr(fld) for fld in migration.fields],
            ['<yepes.data_migrations.fields.DateTimeField: date__datetime (date)>',
             '<yepes.data_migrations.fields.YearField: date__year (date)>',
             '<yepes.data_migrations.fields.MonthField: date__month (date)>',
             '<yepes.data_migrations.fields.DayField: date__day (date)>',
             '<yepes.data_migrations.fields.DateField: datetime__date (datetime)>',
             '<yepes.data_migrations.fields.TimeField: datetime__time (datetime)>',
             '<yepes.data_migrations.fields.YearField: datetime__year (datetime)>',
             '<yepes.data_migrations.fields.MonthField: datetime__month (datetime)>',
             '<yepes.data_migrations.fields.DayField: datetime__day (datetime)>',
             '<yepes.data_migrations.fields.HourField: datetime__hour (datetime)>',
             '<yepes.data_migrations.fields.MinuteField: datetime__minute (datetime)>',
             '<yepes.data_migrations.fields.SecondField: datetime__second (datetime)>',
             '<yepes.data_migrations.fields.MicrosecondField: datetime__microsecond (datetime)>',
             '<yepes.data_migrations.fields.TimeZoneField: datetime__tzinfo (datetime)>',
             '<yepes.data_migrations.fields.HourField: time__hour (time)>',
             '<yepes.data_migrations.fields.MinuteField: time__minute (time)>',
             '<yepes.data_migrations.fields.SecondField: time__second (time)>',
             '<yepes.data_migrations.fields.MicrosecondField: time__microsecond (time)>',
             '<yepes.data_migrations.fields.TimeZoneField: time__tzinfo (time)>'],
        )
        self.assertEqual(
            [repr(fld) for fld in migration.fields_to_import],
            ['<yepes.data_migrations.fields.DateTimeField: date__datetime (date)>',
             '<yepes.data_migrations.fields.YearField: date__year (date)>',
             '<yepes.data_migrations.fields.MonthField: date__month (date)>',
             '<yepes.data_migrations.fields.DayField: date__day (date)>',
             '<yepes.data_migrations.fields.DateField: datetime__date (datetime)>',
             '<yepes.data_migrations.fields.TimeField: datetime__time (datetime)>',
             '<yepes.data_migrations.fields.YearField: datetime__year (datetime)>',
             '<yepes.data_migrations.fields.MonthField: datetime__month (datetime)>',
             '<yepes.data_migrations.fields.DayField: datetime__day (datetime)>',
             '<yepes.data_migrations.fields.HourField: datetime__hour (datetime)>',
             '<yepes.data_migrations.fields.MinuteField: datetime__minute (datetime)>',
             '<yepes.data_migrations.fields.SecondField: datetime__second (datetime)>',
             '<yepes.data_migrations.fields.MicrosecondField: datetime__microsecond (datetime)>',
             '<yepes.data_migrations.fields.TimeZoneField: datetime__tzinfo (datetime)>',
             '<yepes.data_migrations.fields.HourField: time__hour (time)>',
             '<yepes.data_migrations.fields.MinuteField: time__minute (time)>',
             '<yepes.data_migrations.fields.SecondField: time__second (time)>',
             '<yepes.data_migrations.fields.MicrosecondField: time__microsecond (time)>',
             '<yepes.data_migrations.fields.TimeZoneField: time__tzinfo (time)>'],
        )
        self.assertIsNone(migration.primary_key)
        self.assertIsNone(migration.natural_foreign_keys)
        self.assertTrue(migration.can_create)
        self.assertFalse(migration.can_update)
        self.assertFalse(migration.requires_model_instances)

    def test_csv_serializer(self):
        migration = DateTimeMigration(DateTimeModel)
        import_serializer = CsvSerializer
        export_serializer = CsvSerializer(quoting=csv.QUOTE_NONNUMERIC)

        source_path = os.path.join(FIXTURES_DIR, 'datetime_source.csv')
        expected_path = os.path.join(FIXTURES_DIR, 'datetime_result.csv')
        result_path = os.path.join(self.temp_dir, 'datetime_result.csv')

        with open(source_path, 'rb') as source_file:

            with warnings.catch_warnings(record=True) as w:
                warnings.filterwarnings('ignore', 'naive datetime')
                migration.import_data(source_file.read(), import_serializer, DirectPlan)

            objs = list(DateTimeModel.objects.all())
            self.assertEqual(len(objs), len(self.expectedResults))
            for obj, result in zip(objs, self.expectedResults):
                self.assertEqual(obj.date, result[0])
                self.assertEqual(obj.datetime, result[1])
                self.assertEqual(obj.time, result[2])

        with open(expected_path, 'rb') as expected_file:
            with open(result_path, 'wb+') as result_file:

                result = migration.export_data(serializer=export_serializer)
                self.assertEqual(
                        result.splitlines(),
                        expected_file.read().splitlines())

        DateTimeModel.objects.all().delete()
        with open(source_path, 'rb') as source_file:

            with warnings.catch_warnings(record=True) as w:
                warnings.filterwarnings('ignore', 'naive datetime')
                migration.import_data(source_file, import_serializer, DirectPlan)

            objs = list(DateTimeModel.objects.all())
            self.assertEqual(len(objs), len(self.expectedResults))
            for obj, result in zip(objs, self.expectedResults):
                self.assertEqual(obj.date, result[0])
                self.assertEqual(obj.datetime, result[1])
                self.assertEqual(obj.time, result[2])

        with open(expected_path, 'rb') as expected_file:
            with open(result_path, 'wb+') as result_file:

                migration.export_data(result_file, export_serializer)
                result_file.seek(0)
                self.assertEqual(
                        result_file.read().splitlines(),
                        expected_file.read().splitlines())

        migration = DateTimeEdgeMigration(DateTimeModel)
        expected_path = os.path.join(FIXTURES_DIR, 'datetime_edge_result.csv')
        result_path = os.path.join(self.temp_dir, 'datetime_edge_result.csv')
        with open(expected_path, 'rb') as expected_file:
            with open(result_path, 'wb+') as result_file:

                migration.export_data(result_file, export_serializer)
                result_file.seek(0)
                self.assertEqual(
                        result_file.read().splitlines(),
                        expected_file.read().splitlines())

    def test_json_serializer(self):
        migration = DateTimeMigration(DateTimeModel)
        serializer = JsonSerializer

        source_path = os.path.join(FIXTURES_DIR, 'datetime_source.json')
        expected_path = os.path.join(FIXTURES_DIR, 'datetime_result.json')
        result_path = os.path.join(self.temp_dir, 'datetime_result.json')

        with open(source_path, 'rb') as source_file:

            with warnings.catch_warnings(record=True) as w:
                warnings.filterwarnings('ignore', 'naive datetime')
                migration.import_data(source_file.read(), serializer, DirectPlan)

            objs = list(DateTimeModel.objects.all())
            self.assertEqual(len(objs), len(self.expectedResults))
            for obj, result in zip(objs, self.expectedResults):
                self.assertEqual(obj.date, result[0])
                self.assertEqual(obj.datetime, result[1])
                self.assertEqual(obj.time, result[2])

        with open(expected_path, 'rb') as expected_file:
            with open(result_path, 'wb+') as result_file:

                result = migration.export_data(serializer=serializer)
                self.assertEqual(
                        result.splitlines(),
                        expected_file.read().splitlines())

        DateTimeModel.objects.all().delete()
        with open(source_path, 'rb') as source_file:

            with warnings.catch_warnings(record=True) as w:
                warnings.filterwarnings('ignore', 'naive datetime')
                migration.import_data(source_file, serializer, DirectPlan)

            objs = list(DateTimeModel.objects.all())
            self.assertEqual(len(objs), len(self.expectedResults))
            for obj, result in zip(objs, self.expectedResults):
                self.assertEqual(obj.date, result[0])
                self.assertEqual(obj.datetime, result[1])
                self.assertEqual(obj.time, result[2])

        with open(expected_path, 'rb') as expected_file:
            with open(result_path, 'wb+') as result_file:

                migration.export_data(result_file, serializer)
                result_file.seek(0)
                self.assertEqual(
                        result_file.read().splitlines(),
                        expected_file.read().splitlines())

        migration = DateTimeEdgeMigration(DateTimeModel)
        expected_path = os.path.join(FIXTURES_DIR, 'datetime_edge_result.json')
        result_path = os.path.join(self.temp_dir, 'datetime_edge_result.json')
        with open(expected_path, 'rb') as expected_file:
            with open(result_path, 'wb+') as result_file:

                migration.export_data(result_file, serializer)
                result_file.seek(0)
                self.assertEqual(
                        result_file.read().splitlines(),
                        expected_file.read().splitlines())

    def test_tsv_serializer(self):
        migration = DateTimeMigration(DateTimeModel)
        import_serializer = TsvSerializer
        export_serializer = TsvSerializer(quoting=csv.QUOTE_NONNUMERIC)

        source_path = os.path.join(FIXTURES_DIR, 'datetime_source.tsv')
        expected_path = os.path.join(FIXTURES_DIR, 'datetime_result.tsv')
        result_path = os.path.join(self.temp_dir, 'datetime_result.tsv')

        with open(source_path, 'rb') as source_file:

            with warnings.catch_warnings(record=True) as w:
                warnings.filterwarnings('ignore', 'naive datetime')
                migration.import_data(source_file.read(), import_serializer, DirectPlan)

            objs = list(DateTimeModel.objects.all())
            self.assertEqual(len(objs), len(self.expectedResults))
            for obj, result in zip(objs, self.expectedResults):
                self.assertEqual(obj.date, result[0])
                self.assertEqual(obj.datetime, result[1])
                self.assertEqual(obj.time, result[2])

        with open(expected_path, 'rb') as expected_file:
            with open(result_path, 'wb+') as result_file:

                result = migration.export_data(serializer=export_serializer)
                self.assertEqual(
                        result.splitlines(),
                        expected_file.read().splitlines())

        DateTimeModel.objects.all().delete()
        with open(source_path, 'rb') as source_file:

            with warnings.catch_warnings(record=True) as w:
                warnings.filterwarnings('ignore', 'naive datetime')
                migration.import_data(source_file, import_serializer, DirectPlan)

            objs = list(DateTimeModel.objects.all())
            self.assertEqual(len(objs), len(self.expectedResults))
            for obj, result in zip(objs, self.expectedResults):
                self.assertEqual(obj.date, result[0])
                self.assertEqual(obj.datetime, result[1])
                self.assertEqual(obj.time, result[2])

        with open(expected_path, 'rb') as expected_file:
            with open(result_path, 'wb+') as result_file:

                migration.export_data(result_file, export_serializer)
                result_file.seek(0)
                self.assertEqual(
                        result_file.read().splitlines(),
                        expected_file.read().splitlines())

        migration = DateTimeEdgeMigration(DateTimeModel)
        expected_path = os.path.join(FIXTURES_DIR, 'datetime_edge_result.tsv')
        result_path = os.path.join(self.temp_dir, 'datetime_edge_result.tsv')
        with open(expected_path, 'rb') as expected_file:
            with open(result_path, 'wb+') as result_file:

                migration.export_data(result_file, export_serializer)
                result_file.seek(0)
                self.assertEqual(
                        result_file.read().splitlines(),
                        expected_file.read().splitlines())

    def test_yaml_serializer(self):
        migration = DateTimeMigration(DateTimeModel)
        serializer = YamlSerializer

        source_path = os.path.join(FIXTURES_DIR, 'datetime_source.yaml')
        expected_path = os.path.join(FIXTURES_DIR, 'datetime_result.yaml')
        result_path = os.path.join(self.temp_dir, 'datetime_result.yaml')

        with open(source_path, 'rb') as source_file:

            with warnings.catch_warnings(record=True) as w:
                warnings.filterwarnings('ignore', 'naive datetime')
                migration.import_data(source_file.read(), serializer, DirectPlan)

            objs = list(DateTimeModel.objects.all())
            self.assertEqual(len(objs), len(self.expectedResults))
            for obj, result in zip(objs, self.expectedResults):
                self.assertEqual(obj.date, result[0])
                self.assertEqual(obj.datetime, result[1])
                self.assertEqual(obj.time, result[2])

        with open(expected_path, 'rb') as expected_file:
            with open(result_path, 'wb+') as result_file:

                result = migration.export_data(serializer=serializer)
                self.assertEqual(
                        result.splitlines(),
                        expected_file.read().splitlines())

        DateTimeModel.objects.all().delete()
        with open(source_path, 'rb') as source_file:

            with warnings.catch_warnings(record=True) as w:
                warnings.filterwarnings('ignore', 'naive datetime')
                migration.import_data(source_file, serializer, DirectPlan)

            objs = list(DateTimeModel.objects.all())
            self.assertEqual(len(objs), len(self.expectedResults))
            for obj, result in zip(objs, self.expectedResults):
                self.assertEqual(obj.date, result[0])
                self.assertEqual(obj.datetime, result[1])
                self.assertEqual(obj.time, result[2])

        with open(expected_path, 'rb') as expected_file:
            with open(result_path, 'wb+') as result_file:

                migration.export_data(result_file, serializer)
                result_file.seek(0)
                self.assertEqual(
                        result_file.read().splitlines(),
                        expected_file.read().splitlines())

        migration = DateTimeEdgeMigration(DateTimeModel)
        expected_path = os.path.join(FIXTURES_DIR, 'datetime_edge_result.yaml')
        result_path = os.path.join(self.temp_dir, 'datetime_edge_result.yaml')
        with open(expected_path, 'rb') as expected_file:
            with open(result_path, 'wb+') as result_file:

                migration.export_data(result_file, serializer)
                result_file.seek(0)
                self.assertEqual(
                        result_file.read().splitlines(),
                        expected_file.read().splitlines())


class NumberFieldsTests(TempDirMixin, test.TestCase):

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

    def test_data_migration(self):
        migration = NumericMigration(NumericModel)
        self.assertEqual(
            [repr(fld) for fld in migration.fields],
            ['<yepes.data_migrations.fields.IntegerField: integer>',
             '<yepes.data_migrations.fields.IntegerField: integer_as_string>',
             '<yepes.data_migrations.fields.FloatField: float>',
             '<yepes.data_migrations.fields.FloatField: float_as_string>',
             '<yepes.data_migrations.fields.NumberField: decimal>',
             '<yepes.data_migrations.fields.NumberField: decimal_as_string>'],
        )
        self.assertEqual(
            [repr(fld) for fld in migration.fields_to_import],
            ['<yepes.data_migrations.fields.IntegerField: integer>',
             '<yepes.data_migrations.fields.IntegerField: integer_as_string>',
             '<yepes.data_migrations.fields.FloatField: float>',
             '<yepes.data_migrations.fields.FloatField: float_as_string>',
             '<yepes.data_migrations.fields.NumberField: decimal>',
             '<yepes.data_migrations.fields.NumberField: decimal_as_string>'],
        )
        self.assertIsNone(migration.primary_key)
        self.assertIsNone(migration.natural_foreign_keys)
        self.assertTrue(migration.can_create)
        self.assertFalse(migration.can_update)
        self.assertFalse(migration.requires_model_instances)

    def test_csv_serializer(self):
        migration = NumericMigration(NumericModel)
        import_serializer = CsvSerializer
        export_serializer = CsvSerializer(quoting=csv.QUOTE_NONNUMERIC)

        source_path = os.path.join(FIXTURES_DIR, 'numeric_source.csv')
        expected_path = os.path.join(FIXTURES_DIR, 'numeric_result.csv')
        result_path = os.path.join(self.temp_dir, 'numeric_result.csv')

        with open(source_path, 'rb') as source_file:

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

        with open(expected_path, 'rb') as expected_file:
            with open(result_path, 'wb+') as result_file:

                result = migration.export_data(serializer=export_serializer)
                self.assertEqual(
                        result.splitlines(),
                        expected_file.read().splitlines())

        NumericModel.objects.all().delete()
        with open(source_path, 'rb') as source_file:

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

        with open(expected_path, 'rb') as expected_file:
            with open(result_path, 'wb+') as result_file:

                migration.export_data(result_file, export_serializer)
                result_file.seek(0)
                self.assertEqual(
                        result_file.read().splitlines(),
                        expected_file.read().splitlines())

    def test_json_serializer(self):
        migration = NumericMigration(NumericModel)
        serializer = JsonSerializer

        source_path = os.path.join(FIXTURES_DIR, 'numeric_source.json')
        expected_path = os.path.join(FIXTURES_DIR, 'numeric_result.json')
        result_path = os.path.join(self.temp_dir, 'numeric_result.json')

        with open(source_path, 'rb') as source_file:

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

        with open(expected_path, 'rb') as expected_file:
            with open(result_path, 'wb+') as result_file:

                result = migration.export_data(serializer=serializer)
                self.assertEqual(
                        result.splitlines(),
                        expected_file.read().splitlines())

        NumericModel.objects.all().delete()
        with open(source_path, 'rb') as source_file:

            migration.import_data(source_file, serializer, DirectPlan)

            objs = list(NumericModel.objects.all())
            self.assertEqual(len(objs), len(self.expectedResults))
            for obj, result in zip(objs, self.expectedResults):
                self.assertEqual(obj.integer, result[0])
                self.assertEqual(obj.integer_as_string, result[0])
                self.assertEqual(obj.float, result[1])
                self.assertEqual(obj.float_as_string, result[1])
                self.assertEqual(obj.decimal, result[2])
                self.assertEqual(obj.decimal_as_string, result[2])

        with open(expected_path, 'rb') as expected_file:
            with open(result_path, 'wb+') as result_file:

                migration.export_data(result_file, serializer)
                result_file.seek(0)
                self.assertEqual(
                        result_file.read().splitlines(),
                        expected_file.read().splitlines())

    def test_tsv_serializer(self):
        migration = NumericMigration(NumericModel)
        import_serializer = TsvSerializer
        export_serializer = TsvSerializer(quoting=csv.QUOTE_NONNUMERIC)

        source_path = os.path.join(FIXTURES_DIR, 'numeric_source.tsv')
        expected_path = os.path.join(FIXTURES_DIR, 'numeric_result.tsv')
        result_path = os.path.join(self.temp_dir, 'numeric_result.tsv')

        with open(source_path, 'rb') as source_file:

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

        with open(expected_path, 'rb') as expected_file:
            with open(result_path, 'wb+') as result_file:

                result = migration.export_data(serializer=export_serializer)
                self.assertEqual(
                        result.splitlines(),
                        expected_file.read().splitlines())

        NumericModel.objects.all().delete()
        with open(source_path, 'rb') as source_file:

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

        with open(expected_path, 'rb') as expected_file:
            with open(result_path, 'wb+') as result_file:

                migration.export_data(result_file, export_serializer)
                result_file.seek(0)
                self.assertEqual(
                        result_file.read().splitlines(),
                        expected_file.read().splitlines())

    def test_yaml_serializer(self):
        migration = NumericMigration(NumericModel)
        serializer = YamlSerializer

        source_path = os.path.join(FIXTURES_DIR, 'numeric_source.yaml')
        expected_path = os.path.join(FIXTURES_DIR, 'numeric_result.yaml')
        result_path = os.path.join(self.temp_dir, 'numeric_result.yaml')

        with open(source_path, 'rb') as source_file:

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

        with open(expected_path, 'rb') as expected_file:
            with open(result_path, 'wb+') as result_file:

                result = migration.export_data(serializer=serializer)
                self.assertEqual(
                        result.splitlines(),
                        expected_file.read().splitlines())

        NumericModel.objects.all().delete()
        with open(source_path, 'rb') as source_file:

            migration.import_data(source_file, serializer, DirectPlan)

            objs = list(NumericModel.objects.all())
            self.assertEqual(len(objs), len(self.expectedResults))
            for obj, result in zip(objs, self.expectedResults):
                self.assertEqual(obj.integer, result[0])
                self.assertEqual(obj.integer_as_string, result[0])
                self.assertEqual(obj.float, result[1])
                self.assertEqual(obj.float_as_string, result[1])
                self.assertEqual(obj.decimal, result[2])
                self.assertEqual(obj.decimal_as_string, result[2])

        with open(expected_path, 'rb') as expected_file:
            with open(result_path, 'wb+') as result_file:

                migration.export_data(result_file, serializer)
                result_file.seek(0)
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

    def test_data_migration(self):
        migration = TextMigration(TextModel)
        self.assertEqual(
            [repr(fld) for fld in migration.fields],
            ['<yepes.data_migrations.fields.TextField: char>',
             '<yepes.data_migrations.fields.TextField: text>'],
        )
        self.assertEqual(
            [repr(fld) for fld in migration.fields_to_import],
            ['<yepes.data_migrations.fields.TextField: char>',
             '<yepes.data_migrations.fields.TextField: text>'],
        )
        self.assertIsNone(migration.primary_key)
        self.assertIsNone(migration.natural_foreign_keys)
        self.assertTrue(migration.can_create)
        self.assertFalse(migration.can_update)
        self.assertFalse(migration.requires_model_instances)

    def test_csv_serializer(self):
        migration = TextMigration(TextModel)
        import_serializer = CsvSerializer
        export_serializer = CsvSerializer(quoting=csv.QUOTE_NONNUMERIC)

        source_path = os.path.join(FIXTURES_DIR, 'text_source.csv')
        expected_path = os.path.join(FIXTURES_DIR, 'text_result.csv')
        result_path = os.path.join(self.temp_dir, 'text_result.csv')

        with open(source_path, 'rb') as source_file:

            migration.import_data(source_file.read(), import_serializer, DirectPlan)

            objs = list(TextModel.objects.all())
            self.assertEqual(len(objs), len(self.expectedResults))
            for obj, result in zip(objs, self.expectedResults):
                self.assertEqual(obj.char, result)
                self.assertEqual(obj.text, result)

        with open(expected_path, 'rb') as expected_file:
            with open(result_path, 'wb+') as result_file:

                result = migration.export_data(serializer=export_serializer)
                self.assertEqual(
                        result.splitlines(),
                        expected_file.read().splitlines())

        TextModel.objects.all().delete()
        with open(source_path, 'rb') as source_file:

            migration.import_data(source_file, import_serializer, DirectPlan)

            objs = list(TextModel.objects.all())
            self.assertEqual(len(objs), len(self.expectedResults))
            for obj, result in zip(objs, self.expectedResults):
                self.assertEqual(obj.char, result)
                self.assertEqual(obj.text, result)

        with open(expected_path, 'rb') as expected_file:
            with open(result_path, 'wb+') as result_file:

                migration.export_data(result_file, export_serializer)
                result_file.seek(0)
                self.assertEqual(
                        result_file.read().splitlines(),
                        expected_file.read().splitlines())

    def test_json_serializer(self):
        migration = TextMigration(TextModel)
        serializer = JsonSerializer

        source_path = os.path.join(FIXTURES_DIR, 'text_source.json')
        expected_path = os.path.join(FIXTURES_DIR, 'text_result.json')
        result_path = os.path.join(self.temp_dir, 'text_result.json')

        with open(source_path, 'rb') as source_file:

            migration.import_data(source_file.read(), serializer, DirectPlan)

            objs = list(TextModel.objects.all())
            self.assertEqual(len(objs), len(self.expectedResults))
            for obj, result in zip(objs, self.expectedResults):
                self.assertEqual(obj.char, result)
                self.assertEqual(obj.text, result)

        with open(expected_path, 'rb') as expected_file:
            with open(result_path, 'wb+') as result_file:

                result = migration.export_data(serializer=serializer)
                self.assertEqual(
                        result.splitlines(),
                        expected_file.read().splitlines())

        TextModel.objects.all().delete()
        with open(source_path, 'rb') as source_file:

            migration.import_data(source_file, serializer, DirectPlan)

            objs = list(TextModel.objects.all())
            self.assertEqual(len(objs), len(self.expectedResults))
            for obj, result in zip(objs, self.expectedResults):
                self.assertEqual(obj.char, result)
                self.assertEqual(obj.text, result)

        with open(expected_path, 'rb') as expected_file:
            with open(result_path, 'wb+') as result_file:

                migration.export_data(result_file, serializer)
                result_file.seek(0)
                self.assertEqual(
                        result_file.read().splitlines(),
                        expected_file.read().splitlines())

    def test_tsv_serializer(self):
        migration = TextMigration(TextModel)
        import_serializer = TsvSerializer
        export_serializer = TsvSerializer(quoting=csv.QUOTE_NONNUMERIC)

        source_path = os.path.join(FIXTURES_DIR, 'text_source.tsv')
        expected_path = os.path.join(FIXTURES_DIR, 'text_result.tsv')
        result_path = os.path.join(self.temp_dir, 'text_result.tsv')

        with open(source_path, 'rb') as source_file:

            migration.import_data(source_file.read(), import_serializer, DirectPlan)

            objs = list(TextModel.objects.all())
            self.assertEqual(len(objs), len(self.expectedResults))
            for obj, result in zip(objs, self.expectedResults):
                self.assertEqual(obj.char, result)
                self.assertEqual(obj.text, result)

        with open(expected_path, 'rb') as expected_file:
            with open(result_path, 'wb+') as result_file:

                result = migration.export_data(serializer=export_serializer)
                self.assertEqual(
                        result.splitlines(),
                        expected_file.read().splitlines())

        TextModel.objects.all().delete()
        with open(source_path, 'rb') as source_file:

            migration.import_data(source_file, import_serializer, DirectPlan)

            objs = list(TextModel.objects.all())
            self.assertEqual(len(objs), len(self.expectedResults))
            for obj, result in zip(objs, self.expectedResults):
                self.assertEqual(obj.char, result)
                self.assertEqual(obj.text, result)

        with open(expected_path, 'rb') as expected_file:
            with open(result_path, 'wb+') as result_file:

                migration.export_data(result_file, export_serializer)
                result_file.seek(0)
                self.assertEqual(
                        result_file.read().splitlines(),
                        expected_file.read().splitlines())

    def test_yaml_serializer(self):
        migration = TextMigration(TextModel)
        serializer = YamlSerializer

        source_path = os.path.join(FIXTURES_DIR, 'text_source.yaml')
        expected_path = os.path.join(FIXTURES_DIR, 'text_result.yaml')
        result_path = os.path.join(self.temp_dir, 'text_result.yaml')

        with open(source_path, 'rb') as source_file:

            migration.import_data(source_file.read(), serializer, DirectPlan)

            objs = list(TextModel.objects.all())
            self.assertEqual(len(objs), len(self.expectedResults))
            for obj, result in zip(objs, self.expectedResults):
                self.assertEqual(obj.char, result)
                self.assertEqual(obj.text, result)

        with open(expected_path, 'rb') as expected_file:
            with open(result_path, 'wb+') as result_file:

                result = migration.export_data(serializer=serializer)
                self.assertEqual(
                        result.splitlines(),
                        expected_file.read().splitlines())

        TextModel.objects.all().delete()
        with open(source_path, 'rb') as source_file:

            migration.import_data(source_file, serializer, DirectPlan)

            objs = list(TextModel.objects.all())
            self.assertEqual(len(objs), len(self.expectedResults))
            for obj, result in zip(objs, self.expectedResults):
                self.assertEqual(obj.char, result)
                self.assertEqual(obj.text, result)

        with open(expected_path, 'rb') as expected_file:
            with open(result_path, 'wb+') as result_file:

                migration.export_data(result_file, serializer)
                result_file.seek(0)
                self.assertEqual(
                        result_file.read().splitlines(),
                        expected_file.read().splitlines())


class ImportationPlansTests(test.TestCase):

    source_1 = """pk,letter,word\r
1,a,alfa\r
2,b,bravo\r
3,c,charlie\r
4,d,delta\r
5,e,echo\r
"""
    source_2 = """pk,letter,word\r
6,f,foxtrot\r
7,g,golf\r
8,h,hotel\r
9,i,india\r
10,j,juliett\r
"""
    source_3 = """pk,letter,word\r
11,k,kilo\r
12,l,lima\r
13,m,mike\r
14,n,november\r
15,o,oscar\r
"""
    source_4 = """pk,letter,word\r
1,a,alfa\r
2,b,bravo\r
3,c,charlie\r
4,d,delta\r
5,e,echo\r
6,f,frank\r
7,g,george\r
8,h,henry\r
9,i,ida\r
10,j,john\r
11,k,kilo\r
12,l,lima\r
13,m,mike\r
14,n,november\r
15,o,oscar\r
"""
    words_1 = [
        'alfa',
        'bravo',
        'charlie',
        'delta',
        'echo',
    ]
    words_2 = [
        'foxtrot',
        'golf',
        'hotel',
        'india',
        'juliett',
    ]
    words_3 = [
        'kilo',
        'lima',
        'mike',
        'november',
        'oscar',
    ]
    words_4 = [
        'alfa',
        'bravo',
        'charlie',
        'delta',
        'echo',
        'frank',
        'george',
        'henry',
        'ida',
        'john',
        'kilo',
        'lima',
        'mike',
        'november',
        'oscar',
    ]
    maxDiff = None

    def test_data_migration(self):
        migration = AlphabetMigration(AlphabetModel)
        self.assertEqual(
            [repr(fld) for fld in migration.fields],
            ['<yepes.data_migrations.fields.IntegerField: pk>',
             '<yepes.data_migrations.fields.TextField: letter>',
             '<yepes.data_migrations.fields.TextField: word>'],
        )
        self.assertEqual(
            [repr(fld) for fld in migration.fields_to_import],
            ['<yepes.data_migrations.fields.IntegerField: pk>',
             '<yepes.data_migrations.fields.TextField: letter>',
             '<yepes.data_migrations.fields.TextField: word>'],
        )
        self.assertEqual(
            repr(migration.primary_key),
            '<yepes.data_migrations.fields.IntegerField: pk>',
        )
        self.assertIsNone(migration.natural_foreign_keys)
        self.assertTrue(migration.can_create)
        self.assertTrue(migration.can_update)
        self.assertFalse(migration.requires_model_instances)

    def test_direct_plan(self):
        migration = AlphabetMigration(AlphabetModel)
        serializer = 'csv'
        plan = 'direct'
        migration.import_data(self.source_1, serializer, plan)
        objs = AlphabetModel.objects.all()
        self.assertEqual(len(objs), 5)
        for i, word in enumerate(self.words_1):
            obj = objs[i]
            self.assertEqual(obj.pk, i + 1)
            self.assertEqual(obj.letter, word[0])
            self.assertEqual(obj.word, word)

        migration.import_data(self.source_2, serializer, plan)
        objs = AlphabetModel.objects.all()
        self.assertEqual(len(objs), 10)
        for i, word in enumerate(chain(self.words_1, self.words_2)):
            obj = objs[i]
            self.assertEqual(obj.pk, i + 1)
            self.assertEqual(obj.letter, word[0])
            self.assertEqual(obj.word, word)

        with self.assertRaises(Exception):
            migration.import_data(self.source_4, serializer, plan)

        objs = AlphabetModel.objects.all()
        self.assertEqual(len(objs), 10)
        for i, word in enumerate(chain(self.words_1, self.words_2)):
            obj = objs[i]
            self.assertEqual(obj.pk, i + 1)
            self.assertEqual(obj.letter, word[0])
            self.assertEqual(obj.word, word)

    def test_create_plan(self):
        migration = AlphabetMigration(AlphabetModel)
        serializer = 'csv'
        plan = 'create'
        migration.import_data(self.source_1, serializer, plan)
        objs = AlphabetModel.objects.all()
        self.assertEqual(len(objs), 5)
        for i, word in enumerate(self.words_1):
            obj = objs[i]
            self.assertEqual(obj.pk, i + 1)
            self.assertEqual(obj.letter, word[0])
            self.assertEqual(obj.word, word)

        migration.import_data(self.source_2, serializer, plan)
        objs = AlphabetModel.objects.all()
        self.assertEqual(len(objs), 10)
        for i, word in enumerate(chain(self.words_1, self.words_2)):
            obj = objs[i]
            self.assertEqual(obj.pk, i + 1)
            self.assertEqual(obj.letter, word[0])
            self.assertEqual(obj.word, word)

        migration.import_data(self.source_4, serializer, plan)
        objs = AlphabetModel.objects.all()
        self.assertEqual(len(objs), 15)
        for i, word in enumerate(chain(self.words_1, self.words_2, self.words_3)):
            obj = objs[i]
            self.assertEqual(obj.pk, i + 1)
            self.assertEqual(obj.letter, word[0])
            self.assertEqual(obj.word, word)

    def test_bulk_create_plan(self):
        migration = AlphabetMigration(AlphabetModel)
        serializer = 'csv'
        plan = 'bulk_create'
        migration.import_data(self.source_1, serializer, plan)
        objs = AlphabetModel.objects.all()
        self.assertEqual(len(objs), 5)
        for i, word in enumerate(self.words_1):
            obj = objs[i]
            self.assertEqual(obj.pk, i + 1)
            self.assertEqual(obj.letter, word[0])
            self.assertEqual(obj.word, word)

        migration.import_data(self.source_2, serializer, plan)
        objs = AlphabetModel.objects.all()
        self.assertEqual(len(objs), 10)
        for i, word in enumerate(chain(self.words_1, self.words_2)):
            obj = objs[i]
            self.assertEqual(obj.pk, i + 1)
            self.assertEqual(obj.letter, word[0])
            self.assertEqual(obj.word, word)

        migration.import_data(self.source_4, serializer, plan)
        objs = AlphabetModel.objects.all()
        self.assertEqual(len(objs), 15)
        for i, word in enumerate(chain(self.words_1, self.words_2, self.words_3)):
            obj = objs[i]
            self.assertEqual(obj.pk, i + 1)
            self.assertEqual(obj.letter, word[0])
            self.assertEqual(obj.word, word)

    def test_update_plan(self):
        migration = AlphabetMigration(AlphabetModel)
        serializer = 'csv'
        plan = 'update'
        migration.import_data(self.source_1, serializer, plan)
        self.assertEqual(AlphabetModel.objects.count(), 0)

        migration.import_data(self.source_1, serializer, 'direct')
        migration.import_data(self.source_2, serializer, 'direct')
        migration.import_data(self.source_4, serializer, plan)
        objs = AlphabetModel.objects.all()
        self.assertEqual(len(objs), 10)
        for i, word in enumerate(self.words_4):
            if i < 10:
                obj = objs[i]
                self.assertEqual(obj.pk, i + 1)
                self.assertEqual(obj.letter, word[0])
                self.assertEqual(obj.word, word)

    def test_update_or_create_plan(self):
        migration = AlphabetMigration(AlphabetModel)
        serializer = 'csv'
        plan = 'update_or_create'
        migration.import_data(self.source_1, serializer, plan)
        objs = AlphabetModel.objects.all()
        self.assertEqual(len(objs), 5)
        for i, word in enumerate(self.words_1):
            obj = objs[i]
            self.assertEqual(obj.pk, i + 1)
            self.assertEqual(obj.letter, word[0])
            self.assertEqual(obj.word, word)

        migration.import_data(self.source_2, serializer, plan)
        objs = AlphabetModel.objects.all()
        self.assertEqual(len(objs), 10)
        for i, word in enumerate(chain(self.words_1, self.words_2)):
            obj = objs[i]
            self.assertEqual(obj.pk, i + 1)
            self.assertEqual(obj.letter, word[0])
            self.assertEqual(obj.word, word)

        migration.import_data(self.source_4, serializer, plan)
        objs = AlphabetModel.objects.all()
        self.assertEqual(len(objs), 15)
        for i, word in enumerate(self.words_4):
            obj = objs[i]
            self.assertEqual(obj.pk, i + 1)
            self.assertEqual(obj.letter, word[0])
            self.assertEqual(obj.word, word)

    def test_update_or_bulk_create_plan(self):
        migration = AlphabetMigration(AlphabetModel)
        serializer = 'csv'
        plan = 'update_or_bulk_create'
        migration.import_data(self.source_1, serializer, plan)
        objs = AlphabetModel.objects.all()
        self.assertEqual(len(objs), 5)
        for i, word in enumerate(self.words_1):
            obj = objs[i]
            self.assertEqual(obj.pk, i + 1)
            self.assertEqual(obj.letter, word[0])
            self.assertEqual(obj.word, word)

        migration.import_data(self.source_2, serializer, plan)
        objs = AlphabetModel.objects.all()
        self.assertEqual(len(objs), 10)
        for i, word in enumerate(chain(self.words_1, self.words_2)):
            obj = objs[i]
            self.assertEqual(obj.pk, i + 1)
            self.assertEqual(obj.letter, word[0])
            self.assertEqual(obj.word, word)

        migration.import_data(self.source_4, serializer, plan)
        objs = AlphabetModel.objects.all()
        self.assertEqual(len(objs), 15)
        for i, word in enumerate(self.words_4):
            obj = objs[i]
            self.assertEqual(obj.pk, i + 1)
            self.assertEqual(obj.letter, word[0])
            self.assertEqual(obj.word, word)


class NaturalAndCompositeKeysTests(TempDirMixin, test.TestCase):

    maxDiff = None

    def test_data_migrations(self):
        migration = AuthorMigration(AuthorModel)
        self.assertEqual(
            [repr(fld) for fld in migration.fields],
            ['<yepes.data_migrations.fields.TextField: name>'],
        )
        self.assertEqual(
            [repr(fld) for fld in migration.fields_to_import],
            ['<yepes.data_migrations.fields.TextField: name>'],
        )
        self.assertEqual(
            repr(migration.primary_key),
            '<yepes.data_migrations.fields.TextField: name>',
        )
        self.assertIsNone(migration.natural_foreign_keys)
        self.assertTrue(migration.can_create)
        self.assertTrue(migration.can_update)
        self.assertFalse(migration.requires_model_instances)

        migration = BlogMigration(BlogModel)
        self.assertEqual(
            [repr(fld) for fld in migration.fields],
            ['<yepes.data_migrations.fields.TextField: name>',
             '<yepes.data_migrations.fields.TextField: description>'],
        )
        self.assertEqual(
            [repr(fld) for fld in migration.fields_to_import],
            ['<yepes.data_migrations.fields.TextField: name>',
             '<yepes.data_migrations.fields.TextField: description>'],
        )
        self.assertEqual(
            repr(migration.primary_key),
            '<yepes.data_migrations.fields.TextField: name>',
        )
        self.assertIsNone(migration.natural_foreign_keys)
        self.assertTrue(migration.can_create)
        self.assertTrue(migration.can_update)
        self.assertFalse(migration.requires_model_instances)

        migration = BlogCategoryMigration(BlogCategoryModel)
        self.assertEqual(
            [repr(fld) for fld in migration.fields],
            ['<yepes.data_migrations.fields.TextField: blog__name>',
             '<yepes.data_migrations.fields.TextField: name>',
             '<yepes.data_migrations.fields.TextField: description>'],
        )
        self.assertEqual(
            [repr(fld) for fld in migration.fields_to_import],
            ['<yepes.data_migrations.fields.TextField: blog__name>',
             '<yepes.data_migrations.fields.TextField: name>',
             '<yepes.data_migrations.fields.TextField: description>'],
        )
        self.assertEqual(
            [repr(k) for k in migration.primary_key],
            ['<yepes.data_migrations.fields.TextField: blog__name>',
             '<yepes.data_migrations.fields.TextField: name>'],
        )
        self.assertEqual(
            [repr(k) for k in migration.natural_foreign_keys],
            ['<yepes.data_migrations.fields.TextField: blog__name>'],
        )
        self.assertTrue(migration.can_create)
        self.assertTrue(migration.can_update)
        self.assertFalse(migration.requires_model_instances)

    def test_create_and_update_plans(self):
        migration = AuthorMigration(AuthorModel)
        self.assertEqual(migration.primary_key.path, 'name')

        source_path = os.path.join(FIXTURES_DIR, 'author_source.json')
        with open(source_path, 'rb') as source_file:

            migration.import_data(source_file.read(), plan='create')
            result = migration.export_data()
            source_file.seek(0)
            self.assertEqual(
                    result.splitlines(),
                    source_file.read().splitlines())

        migration = BlogMigration(BlogModel)
        self.assertEqual(migration.primary_key.path, 'name')

        source_path = os.path.join(FIXTURES_DIR, 'blog_source.json')
        update_path = os.path.join(FIXTURES_DIR, 'blog_update.json')
        expected_path = os.path.join(FIXTURES_DIR, 'blog_result.json')
        result_path = os.path.join(self.temp_dir, 'blog_result.json')
        with open(source_path, 'rb') as source_file:
            with open(update_path, 'rb') as update_file:
                with open(expected_path, 'rb') as expected_file:
                    with open(result_path, 'wb+') as result_file:

                        migration.import_data(source_file.read(), plan='create')
                        migration.import_data(update_file.read(), plan='create')
                        result = migration.export_data()
                        source_file.seek(0)
                        update_file.seek(0)
                        self.assertEqual(
                                result.splitlines(),
                                source_file.read().splitlines())

                        migration.import_data(update_file.read(), plan='update')
                        result = migration.export_data()
                        self.assertEqual(
                                result.splitlines(),
                                expected_file.read().splitlines())

        migration = BlogCategoryMigration(BlogCategoryModel)
        self.assertIsInstance(migration.primary_key, collections.Iterable)
        self.assertEqual(
            [k.path for k in migration.primary_key],
            ['blog__name', 'name'],
        )
        self.assertEqual(
            [k.attname for k in migration.primary_key],
            ['blog_id', 'name'],
        )
        source_path = os.path.join(FIXTURES_DIR, 'blog_category_source.json')
        update_path = os.path.join(FIXTURES_DIR, 'blog_category_update.json')
        expected_path = os.path.join(FIXTURES_DIR, 'blog_category_result.json')
        result_path = os.path.join(self.temp_dir, 'blog_category_result.json')
        with open(source_path, 'rb') as source_file:
            with open(update_path, 'rb') as update_file:
                with open(expected_path, 'rb') as expected_file:
                    with open(result_path, 'wb+') as result_file:

                        migration.import_data(source_file.read(), plan='create')
                        migration.import_data(update_file.read(), plan='create')
                        result = migration.export_data()
                        source_file.seek(0)
                        update_file.seek(0)
                        self.assertEqual(
                                result.splitlines(),
                                source_file.read().splitlines())

                        migration.import_data(update_file.read(), plan='update')
                        result = migration.export_data()
                        self.assertEqual(
                                result.splitlines(),
                                expected_file.read().splitlines())

    def test_bulk_create_and_update_plans(self):
        migration = AuthorMigration(AuthorModel)
        self.assertEqual(migration.primary_key.path, 'name')

        source_path = os.path.join(FIXTURES_DIR, 'author_source.json')
        with open(source_path, 'rb') as source_file:

            migration.import_data(source_file.read(), plan='bulk_create')
            result = migration.export_data()
            source_file.seek(0)
            self.assertEqual(
                    result.splitlines(),
                    source_file.read().splitlines())

        migration = BlogMigration(BlogModel)
        self.assertEqual(migration.primary_key.path, 'name')

        source_path = os.path.join(FIXTURES_DIR, 'blog_source.json')
        update_path = os.path.join(FIXTURES_DIR, 'blog_update.json')
        expected_path = os.path.join(FIXTURES_DIR, 'blog_result.json')
        result_path = os.path.join(self.temp_dir, 'blog_result.json')
        with open(source_path, 'rb') as source_file:
            with open(update_path, 'rb') as update_file:
                with open(expected_path, 'rb') as expected_file:
                    with open(result_path, 'wb+') as result_file:

                        migration.import_data(source_file.read(), plan='bulk_create')
                        migration.import_data(update_file.read(), plan='bulk_create')
                        result = migration.export_data()
                        source_file.seek(0)
                        update_file.seek(0)
                        self.assertEqual(
                                result.splitlines(),
                                source_file.read().splitlines())

                        migration.import_data(update_file.read(), plan='update')
                        result = migration.export_data()
                        self.assertEqual(
                                result.splitlines(),
                                expected_file.read().splitlines())

        migration = BlogCategoryMigration(BlogCategoryModel)
        self.assertIsInstance(migration.primary_key, collections.Iterable)
        self.assertEqual(
            [k.path for k in migration.primary_key],
            ['blog__name', 'name'],
        )
        self.assertEqual(
            [k.attname for k in migration.primary_key],
            ['blog_id', 'name'],
        )
        source_path = os.path.join(FIXTURES_DIR, 'blog_category_source.json')
        update_path = os.path.join(FIXTURES_DIR, 'blog_category_update.json')
        expected_path = os.path.join(FIXTURES_DIR, 'blog_category_result.json')
        result_path = os.path.join(self.temp_dir, 'blog_category_result.json')
        with open(source_path, 'rb') as source_file:
            with open(update_path, 'rb') as update_file:
                with open(expected_path, 'rb') as expected_file:
                    with open(result_path, 'wb+') as result_file:

                        migration.import_data(source_file.read(), plan='bulk_create')
                        migration.import_data(update_file.read(), plan='bulk_create')
                        result = migration.export_data()
                        source_file.seek(0)
                        update_file.seek(0)
                        self.assertEqual(
                                result.splitlines(),
                                source_file.read().splitlines())

                        migration.import_data(update_file.read(), plan='update')
                        result = migration.export_data()
                        self.assertEqual(
                                result.splitlines(),
                                expected_file.read().splitlines())

    def test_update_or_create_plan(self):
        migration = AuthorMigration(AuthorModel)
        self.assertEqual(migration.primary_key.path, 'name')

        source_path = os.path.join(FIXTURES_DIR, 'author_source.json')
        with open(source_path, 'rb') as source_file:

            migration.import_data(source_file.read())
            result = migration.export_data()
            source_file.seek(0)
            self.assertEqual(
                    result.splitlines(),
                    source_file.read().splitlines())

        migration = BlogMigration(BlogModel)
        self.assertEqual(migration.primary_key.path, 'name')

        source_path = os.path.join(FIXTURES_DIR, 'blog_source.json')
        update_path = os.path.join(FIXTURES_DIR, 'blog_update.json')
        expected_path = os.path.join(FIXTURES_DIR, 'blog_result.json')
        result_path = os.path.join(self.temp_dir, 'blog_result.json')
        with open(source_path, 'rb') as source_file:
            with open(update_path, 'rb') as update_file:
                with open(expected_path, 'rb') as expected_file:
                    with open(result_path, 'wb+') as result_file:

                        migration.import_data(source_file.read())
                        migration.import_data(update_file.read())
                        result = migration.export_data()
                        self.assertEqual(
                                result.splitlines(),
                                expected_file.read().splitlines())

        migration = BlogCategoryMigration(BlogCategoryModel)
        self.assertIsInstance(migration.primary_key, collections.Iterable)
        self.assertEqual(
            [k.path for k in migration.primary_key],
            ['blog__name', 'name'],
        )
        self.assertEqual(
            [k.attname for k in migration.primary_key],
            ['blog_id', 'name'],
        )
        source_path = os.path.join(FIXTURES_DIR, 'blog_category_source.json')
        update_path = os.path.join(FIXTURES_DIR, 'blog_category_update.json')
        expected_path = os.path.join(FIXTURES_DIR, 'blog_category_result.json')
        result_path = os.path.join(self.temp_dir, 'blog_category_result.json')
        with open(source_path, 'rb') as source_file:
            with open(update_path, 'rb') as update_file:
                with open(expected_path, 'rb') as expected_file:
                    with open(result_path, 'wb+') as result_file:

                        migration.import_data(source_file.read())
                        migration.import_data(update_file.read())
                        result = migration.export_data()
                        self.assertEqual(
                                result.splitlines(),
                                expected_file.read().splitlines())

    def test_update_or_bulk_create_plan(self):
        migration = AuthorMigration(AuthorModel)
        self.assertEqual(migration.primary_key.path, 'name')

        source_path = os.path.join(FIXTURES_DIR, 'author_source.json')
        with open(source_path, 'rb') as source_file:

            migration.import_data(source_file.read(), plan='update_or_bulk_create')
            result = migration.export_data()
            source_file.seek(0)
            self.assertEqual(
                    result.splitlines(),
                    source_file.read().splitlines())

        migration = BlogMigration(BlogModel)
        self.assertEqual(migration.primary_key.path, 'name')

        source_path = os.path.join(FIXTURES_DIR, 'blog_source.json')
        update_path = os.path.join(FIXTURES_DIR, 'blog_update.json')
        expected_path = os.path.join(FIXTURES_DIR, 'blog_result.json')
        result_path = os.path.join(self.temp_dir, 'blog_result.json')
        with open(source_path, 'rb') as source_file:
            with open(update_path, 'rb') as update_file:
                with open(expected_path, 'rb') as expected_file:
                    with open(result_path, 'wb+') as result_file:

                        migration.import_data(source_file.read(), plan='update_or_bulk_create')
                        migration.import_data(update_file.read(), plan='update_or_bulk_create')
                        result = migration.export_data()
                        self.assertEqual(
                                result.splitlines(),
                                expected_file.read().splitlines())

        migration = BlogCategoryMigration(BlogCategoryModel)
        self.assertIsInstance(migration.primary_key, collections.Iterable)
        self.assertEqual(
            [k.path for k in migration.primary_key],
            ['blog__name', 'name'],
        )
        self.assertEqual(
            [k.attname for k in migration.primary_key],
            ['blog_id', 'name'],
        )
        source_path = os.path.join(FIXTURES_DIR, 'blog_category_source.json')
        update_path = os.path.join(FIXTURES_DIR, 'blog_category_update.json')
        expected_path = os.path.join(FIXTURES_DIR, 'blog_category_result.json')
        result_path = os.path.join(self.temp_dir, 'blog_category_result.json')
        with open(source_path, 'rb') as source_file:
            with open(update_path, 'rb') as update_file:
                with open(expected_path, 'rb') as expected_file:
                    with open(result_path, 'wb+') as result_file:

                        migration.import_data(source_file.read(), plan='update_or_bulk_create')
                        migration.import_data(update_file.read(), plan='update_or_bulk_create')
                        result = migration.export_data()
                        self.assertEqual(
                                result.splitlines(),
                                expected_file.read().splitlines())


class ModelMigrationsTests(test.TestCase):

    maxDiff = None

    def test_alphabet_model(self):
        migration = DataMigration(AlphabetModel)
        self.assertEqual(
            [repr(fld) for fld in migration.fields],
            ['<yepes.data_migrations.fields.IntegerField: id>',
             '<yepes.data_migrations.fields.TextField: letter>',
             '<yepes.data_migrations.fields.TextField: word>'],
        )
        self.assertEqual(
            [repr(fld) for fld in migration.fields_to_import],
            ['<yepes.data_migrations.fields.IntegerField: id>',
             '<yepes.data_migrations.fields.TextField: letter>',
             '<yepes.data_migrations.fields.TextField: word>'],
        )
        self.assertEqual(
            repr(migration.primary_key),
            '<yepes.data_migrations.fields.IntegerField: id>',
        )
        self.assertIsNone(migration.natural_foreign_keys)
        self.assertTrue(migration.can_create)
        self.assertTrue(migration.can_update)
        self.assertFalse(migration.requires_model_instances)

        migration = DataMigration(
            AlphabetModel,
            use_natural_primary_keys=True,
            use_natural_foreign_keys=True,
        )
        self.assertEqual(
            [repr(fld) for fld in migration.fields],
            ['<yepes.data_migrations.fields.TextField: letter>',
             '<yepes.data_migrations.fields.TextField: word>'],
        )
        self.assertEqual(
            [repr(fld) for fld in migration.fields_to_import],
            ['<yepes.data_migrations.fields.TextField: letter>',
             '<yepes.data_migrations.fields.TextField: word>'],
        )
        self.assertEqual(
            repr(migration.primary_key),
            '<yepes.data_migrations.fields.TextField: letter>',
        )
        self.assertIsNone(migration.natural_foreign_keys)
        self.assertTrue(migration.can_create)
        self.assertTrue(migration.can_update)
        self.assertFalse(migration.requires_model_instances)

    def test_author_model(self):
        migration = DataMigration(AuthorModel)
        self.assertEqual(
            [repr(fld) for fld in migration.fields],
            ['<yepes.data_migrations.fields.IntegerField: id>',
             '<yepes.data_migrations.fields.TextField: name>'],
        )
        self.assertEqual(
            [repr(fld) for fld in migration.fields_to_import],
            ['<yepes.data_migrations.fields.IntegerField: id>',
             '<yepes.data_migrations.fields.TextField: name>'],
        )
        self.assertEqual(
            repr(migration.primary_key),
            '<yepes.data_migrations.fields.IntegerField: id>',
        )
        self.assertIsNone(migration.natural_foreign_keys)
        self.assertTrue(migration.can_create)
        self.assertTrue(migration.can_update)
        self.assertFalse(migration.requires_model_instances)

        migration = DataMigration(
            AuthorModel,
            use_natural_primary_keys=True,
            use_natural_foreign_keys=True,
        )
        self.assertEqual(
            [repr(fld) for fld in migration.fields],
            ['<yepes.data_migrations.fields.TextField: name>'],
        )
        self.assertEqual(
            [repr(fld) for fld in migration.fields_to_import],
            ['<yepes.data_migrations.fields.TextField: name>'],
        )
        self.assertEqual(
            repr(migration.primary_key),
            '<yepes.data_migrations.fields.TextField: name>',
        )
        self.assertIsNone(migration.natural_foreign_keys)
        self.assertTrue(migration.can_create)
        self.assertTrue(migration.can_update)
        self.assertFalse(migration.requires_model_instances)

    def test_blog_model(self):
        migration = DataMigration(BlogModel)
        self.assertEqual(
            [repr(fld) for fld in migration.fields],
            ['<yepes.data_migrations.fields.IntegerField: id>',
             '<yepes.data_migrations.fields.TextField: name>',
             '<yepes.data_migrations.fields.TextField: description>'],
        )
        self.assertEqual(
            [repr(fld) for fld in migration.fields_to_import],
            ['<yepes.data_migrations.fields.IntegerField: id>',
             '<yepes.data_migrations.fields.TextField: name>',
             '<yepes.data_migrations.fields.TextField: description>'],
        )
        self.assertEqual(
            repr(migration.primary_key),
            '<yepes.data_migrations.fields.IntegerField: id>',
        )
        self.assertIsNone(migration.natural_foreign_keys)
        self.assertTrue(migration.can_create)
        self.assertTrue(migration.can_update)
        self.assertFalse(migration.requires_model_instances)

        migration = DataMigration(
            BlogModel,
            use_natural_primary_keys=True,
            use_natural_foreign_keys=True,
        )
        self.assertEqual(
            [repr(fld) for fld in migration.fields],
            ['<yepes.data_migrations.fields.TextField: name>',
             '<yepes.data_migrations.fields.TextField: description>'],
        )
        self.assertEqual(
            [repr(fld) for fld in migration.fields_to_import],
            ['<yepes.data_migrations.fields.TextField: name>',
             '<yepes.data_migrations.fields.TextField: description>'],
        )
        self.assertEqual(
            repr(migration.primary_key),
            '<yepes.data_migrations.fields.TextField: name>',
        )
        self.assertIsNone(migration.natural_foreign_keys)
        self.assertTrue(migration.can_create)
        self.assertTrue(migration.can_update)
        self.assertFalse(migration.requires_model_instances)

    def test_blog_category_model(self):
        migration = DataMigration(BlogCategoryModel)
        self.assertEqual(
            [repr(fld) for fld in migration.fields],
            ['<yepes.data_migrations.fields.IntegerField: id>',
             '<yepes.data_migrations.fields.IntegerField: blog (blog_id)>',
             '<yepes.data_migrations.fields.TextField: name>',
             '<yepes.data_migrations.fields.TextField: description>'],
        )
        self.assertEqual(
            [repr(fld) for fld in migration.fields_to_import],
            ['<yepes.data_migrations.fields.IntegerField: id>',
             '<yepes.data_migrations.fields.IntegerField: blog (blog_id)>',
             '<yepes.data_migrations.fields.TextField: name>',
             '<yepes.data_migrations.fields.TextField: description>'],
        )
        self.assertEqual(
            repr(migration.primary_key),
            '<yepes.data_migrations.fields.IntegerField: id>',
        )
        self.assertIsNone(migration.natural_foreign_keys)
        self.assertTrue(migration.can_create)
        self.assertTrue(migration.can_update)
        self.assertFalse(migration.requires_model_instances)

    def test_boolean_migration(self):
        migration = DataMigration(BooleanModel)
        self.assertEqual(
            [repr(fld) for fld in migration.fields],
            ['<yepes.data_migrations.fields.IntegerField: id>',
             '<yepes.data_migrations.fields.BooleanField: boolean>',
             '<yepes.data_migrations.fields.BooleanField: boolean_as_string>',
             '<yepes.data_migrations.fields.BooleanField: null_boolean>',
             '<yepes.data_migrations.fields.BooleanField: null_boolean_as_string>'],
        )
        self.assertEqual(
            [repr(fld) for fld in migration.fields_to_import],
            ['<yepes.data_migrations.fields.IntegerField: id>',
             '<yepes.data_migrations.fields.BooleanField: boolean>',
             '<yepes.data_migrations.fields.BooleanField: boolean_as_string>',
             '<yepes.data_migrations.fields.BooleanField: null_boolean>',
             '<yepes.data_migrations.fields.BooleanField: null_boolean_as_string>'],
        )
        self.assertEqual(
            repr(migration.primary_key),
            '<yepes.data_migrations.fields.IntegerField: id>',
        )
        self.assertIsNone(migration.natural_foreign_keys)
        self.assertTrue(migration.can_create)
        self.assertTrue(migration.can_update)
        self.assertFalse(migration.requires_model_instances)

        migration = DataMigration(
            BooleanModel,
            use_natural_primary_keys=True,
            use_natural_foreign_keys=True,
        )
        self.assertEqual(
            [repr(fld) for fld in migration.fields],
            ['<yepes.data_migrations.fields.IntegerField: id>',
             '<yepes.data_migrations.fields.BooleanField: boolean>',
             '<yepes.data_migrations.fields.BooleanField: boolean_as_string>',
             '<yepes.data_migrations.fields.BooleanField: null_boolean>',
             '<yepes.data_migrations.fields.BooleanField: null_boolean_as_string>'],
        )
        self.assertEqual(
            [repr(fld) for fld in migration.fields_to_import],
            ['<yepes.data_migrations.fields.IntegerField: id>',
             '<yepes.data_migrations.fields.BooleanField: boolean>',
             '<yepes.data_migrations.fields.BooleanField: boolean_as_string>',
             '<yepes.data_migrations.fields.BooleanField: null_boolean>',
             '<yepes.data_migrations.fields.BooleanField: null_boolean_as_string>'],
        )
        self.assertEqual(
            repr(migration.primary_key),
            '<yepes.data_migrations.fields.IntegerField: id>',
        )
        self.assertIsNone(migration.natural_foreign_keys)
        self.assertTrue(migration.can_create)
        self.assertTrue(migration.can_update)
        self.assertFalse(migration.requires_model_instances)

    def test_datetime_model(self):
        migration = DataMigration(DateTimeModel)
        self.assertEqual(
            [repr(fld) for fld in migration.fields],
            ['<yepes.data_migrations.fields.IntegerField: id>',
             '<yepes.data_migrations.fields.DateField: date>',
             '<yepes.data_migrations.fields.DateTimeField: datetime>',
             '<yepes.data_migrations.fields.TimeField: time>'],
        )
        self.assertEqual(
            [repr(fld) for fld in migration.fields_to_import],
            ['<yepes.data_migrations.fields.IntegerField: id>',
             '<yepes.data_migrations.fields.DateField: date>',
             '<yepes.data_migrations.fields.DateTimeField: datetime>',
             '<yepes.data_migrations.fields.TimeField: time>'],
        )
        self.assertEqual(
            repr(migration.primary_key),
            '<yepes.data_migrations.fields.IntegerField: id>',
        )
        self.assertIsNone(migration.natural_foreign_keys)
        self.assertTrue(migration.can_create)
        self.assertTrue(migration.can_update)
        self.assertFalse(migration.requires_model_instances)

        migration = DataMigration(
            DateTimeModel,
            use_natural_primary_keys=True,
            use_natural_foreign_keys=True,
        )
        self.assertEqual(
            [repr(fld) for fld in migration.fields],
            ['<yepes.data_migrations.fields.IntegerField: id>',
             '<yepes.data_migrations.fields.DateField: date>',
             '<yepes.data_migrations.fields.DateTimeField: datetime>',
             '<yepes.data_migrations.fields.TimeField: time>'],
        )
        self.assertEqual(
            [repr(fld) for fld in migration.fields_to_import],
            ['<yepes.data_migrations.fields.IntegerField: id>',
             '<yepes.data_migrations.fields.DateField: date>',
             '<yepes.data_migrations.fields.DateTimeField: datetime>',
             '<yepes.data_migrations.fields.TimeField: time>'],
        )
        self.assertEqual(
            repr(migration.primary_key),
            '<yepes.data_migrations.fields.IntegerField: id>',
        )
        self.assertIsNone(migration.natural_foreign_keys)
        self.assertTrue(migration.can_create)
        self.assertTrue(migration.can_update)
        self.assertFalse(migration.requires_model_instances)

    def test_numeric_model(self):
        migration = DataMigration(NumericModel)
        self.assertEqual(
            [repr(fld) for fld in migration.fields],
            ['<yepes.data_migrations.fields.IntegerField: id>',
             '<yepes.data_migrations.fields.IntegerField: integer>',
             '<yepes.data_migrations.fields.IntegerField: integer_as_string>',
             '<yepes.data_migrations.fields.FloatField: float>',
             '<yepes.data_migrations.fields.FloatField: float_as_string>',
             '<yepes.data_migrations.fields.NumberField: decimal>',
             '<yepes.data_migrations.fields.NumberField: decimal_as_string>'],
        )
        self.assertEqual(
            [repr(fld) for fld in migration.fields_to_import],
            ['<yepes.data_migrations.fields.IntegerField: id>',
             '<yepes.data_migrations.fields.IntegerField: integer>',
             '<yepes.data_migrations.fields.IntegerField: integer_as_string>',
             '<yepes.data_migrations.fields.FloatField: float>',
             '<yepes.data_migrations.fields.FloatField: float_as_string>',
             '<yepes.data_migrations.fields.NumberField: decimal>',
             '<yepes.data_migrations.fields.NumberField: decimal_as_string>'],
        )
        self.assertEqual(
            repr(migration.primary_key),
            '<yepes.data_migrations.fields.IntegerField: id>',
        )
        self.assertIsNone(migration.natural_foreign_keys)
        self.assertTrue(migration.can_create)
        self.assertTrue(migration.can_update)
        self.assertFalse(migration.requires_model_instances)

        migration = DataMigration(
            NumericModel,
            use_natural_primary_keys=True,
            use_natural_foreign_keys=True,
        )
        self.assertEqual(
            [repr(fld) for fld in migration.fields],
            ['<yepes.data_migrations.fields.IntegerField: id>',
             '<yepes.data_migrations.fields.IntegerField: integer>',
             '<yepes.data_migrations.fields.IntegerField: integer_as_string>',
             '<yepes.data_migrations.fields.FloatField: float>',
             '<yepes.data_migrations.fields.FloatField: float_as_string>',
             '<yepes.data_migrations.fields.NumberField: decimal>',
             '<yepes.data_migrations.fields.NumberField: decimal_as_string>'],
        )
        self.assertEqual(
            [repr(fld) for fld in migration.fields_to_import],
            ['<yepes.data_migrations.fields.IntegerField: id>',
             '<yepes.data_migrations.fields.IntegerField: integer>',
             '<yepes.data_migrations.fields.IntegerField: integer_as_string>',
             '<yepes.data_migrations.fields.FloatField: float>',
             '<yepes.data_migrations.fields.FloatField: float_as_string>',
             '<yepes.data_migrations.fields.NumberField: decimal>',
             '<yepes.data_migrations.fields.NumberField: decimal_as_string>'],
        )
        self.assertEqual(
            repr(migration.primary_key),
            '<yepes.data_migrations.fields.IntegerField: id>',
        )
        self.assertIsNone(migration.natural_foreign_keys)
        self.assertTrue(migration.can_create)
        self.assertTrue(migration.can_update)
        self.assertFalse(migration.requires_model_instances)

    def test_text_model(self):
        migration = DataMigration(TextModel)
        self.assertEqual(
            [repr(fld) for fld in migration.fields],
            ['<yepes.data_migrations.fields.IntegerField: id>',
             '<yepes.data_migrations.fields.TextField: char>',
             '<yepes.data_migrations.fields.TextField: text>'],
        )
        self.assertEqual(
            [repr(fld) for fld in migration.fields_to_import],
            ['<yepes.data_migrations.fields.IntegerField: id>',
             '<yepes.data_migrations.fields.TextField: char>',
             '<yepes.data_migrations.fields.TextField: text>'],
        )
        self.assertEqual(
            repr(migration.primary_key),
            '<yepes.data_migrations.fields.IntegerField: id>',
        )
        self.assertIsNone(migration.natural_foreign_keys)
        self.assertTrue(migration.can_create)
        self.assertTrue(migration.can_update)
        self.assertFalse(migration.requires_model_instances)

        migration = DataMigration(
            TextModel,
            use_natural_primary_keys=True,
            use_natural_foreign_keys=True,
        )
        self.assertEqual(
            [repr(fld) for fld in migration.fields],
            ['<yepes.data_migrations.fields.IntegerField: id>',
             '<yepes.data_migrations.fields.TextField: char>',
             '<yepes.data_migrations.fields.TextField: text>'],
        )
        self.assertEqual(
            [repr(fld) for fld in migration.fields_to_import],
            ['<yepes.data_migrations.fields.IntegerField: id>',
             '<yepes.data_migrations.fields.TextField: char>',
             '<yepes.data_migrations.fields.TextField: text>'],
        )
        self.assertEqual(
            repr(migration.primary_key),
            '<yepes.data_migrations.fields.IntegerField: id>',
        )
        self.assertIsNone(migration.natural_foreign_keys)
        self.assertTrue(migration.can_create)
        self.assertTrue(migration.can_update)
        self.assertFalse(migration.requires_model_instances)

    def test_filter_migration_fields(self):
        migration = DataMigration(BooleanModel, fields=[
            'pk',
            'null_boolean',
            'boolean',
        ], exclude=[
            'pk',
        ])
        self.assertEqual(
            [repr(fld) for fld in migration.fields],
            ['<yepes.data_migrations.fields.BooleanField: null_boolean>',
             '<yepes.data_migrations.fields.BooleanField: boolean>'],
        )
        self.assertEqual(
            [repr(fld) for fld in migration.fields_to_import],
            ['<yepes.data_migrations.fields.BooleanField: null_boolean>',
             '<yepes.data_migrations.fields.BooleanField: boolean>'],
        )
        self.assertIsNone(migration.primary_key)
        self.assertIsNone(migration.natural_foreign_keys)
        self.assertTrue(migration.can_create)
        self.assertFalse(migration.can_update)
        self.assertFalse(migration.requires_model_instances)

    def test_natural_keys(self):
        migration = DataMigration(
            BlogCategoryModel,
            use_natural_primary_keys=True,
            use_natural_foreign_keys=False,
        )
        self.assertEqual(
            [repr(fld) for fld in migration.fields],
            ['<yepes.data_migrations.fields.IntegerField: blog (blog_id)>',
             '<yepes.data_migrations.fields.TextField: name>',
             '<yepes.data_migrations.fields.TextField: description>'],
        )
        self.assertEqual(
            [repr(fld) for fld in migration.fields_to_import],
            ['<yepes.data_migrations.fields.IntegerField: blog (blog_id)>',
             '<yepes.data_migrations.fields.TextField: name>',
             '<yepes.data_migrations.fields.TextField: description>'],
        )
        self.assertEqual(
            [repr(fld) for fld in migration.primary_key],
            ['<yepes.data_migrations.fields.IntegerField: blog (blog_id)>',
             '<yepes.data_migrations.fields.TextField: name>'],
        )
        self.assertIsNone(migration.natural_foreign_keys)
        self.assertTrue(migration.can_create)
        self.assertTrue(migration.can_update)
        self.assertFalse(migration.requires_model_instances)

        migration = DataMigration(
            BlogCategoryModel,
            use_natural_primary_keys=False,
            use_natural_foreign_keys=True,
        )
        self.assertEqual(
            [repr(fld) for fld in migration.fields],
            ['<yepes.data_migrations.fields.IntegerField: id>',
             '<yepes.data_migrations.fields.TextField: blog__name>',
             '<yepes.data_migrations.fields.TextField: name>',
             '<yepes.data_migrations.fields.TextField: description>'],
        )
        self.assertEqual(
            [repr(fld) for fld in migration.fields_to_import],
            ['<yepes.data_migrations.fields.IntegerField: id>',
             '<yepes.data_migrations.fields.TextField: blog__name>',
             '<yepes.data_migrations.fields.TextField: name>',
             '<yepes.data_migrations.fields.TextField: description>'],
        )
        self.assertEqual(
            repr(migration.primary_key),
            '<yepes.data_migrations.fields.IntegerField: id>',
        )
        self.assertEqual(
            [repr(fld) for fld in migration.natural_foreign_keys],
            ['<yepes.data_migrations.fields.TextField: blog__name>'],
        )
        self.assertTrue(migration.can_create)
        self.assertTrue(migration.can_update)
        self.assertFalse(migration.requires_model_instances)

        migration = DataMigration(
            BlogCategoryModel,
            use_natural_primary_keys=True,
            use_natural_foreign_keys=True,
        )
        self.assertEqual(
            [repr(fld) for fld in migration.fields],
            ['<yepes.data_migrations.fields.TextField: blog__name>',
             '<yepes.data_migrations.fields.TextField: name>',
             '<yepes.data_migrations.fields.TextField: description>'],
        )
        self.assertEqual(
            [repr(fld) for fld in migration.fields_to_import],
            ['<yepes.data_migrations.fields.TextField: blog__name>',
             '<yepes.data_migrations.fields.TextField: name>',
             '<yepes.data_migrations.fields.TextField: description>'],
        )
        self.assertEqual(
            [repr(fld) for fld in migration.primary_key],
            ['<yepes.data_migrations.fields.TextField: blog__name>',
             '<yepes.data_migrations.fields.TextField: name>'],
        )
        self.assertEqual(
            [repr(fld) for fld in migration.natural_foreign_keys],
            ['<yepes.data_migrations.fields.TextField: blog__name>'],
        )
        self.assertTrue(migration.can_create)
        self.assertTrue(migration.can_update)
        self.assertFalse(migration.requires_model_instances)


class QuerySetExportationsTests(TempDirMixin, test.TestCase):

    maxDiff = None

    def setUp(self):
        migration = BlogMigration(BlogModel)
        source_path = os.path.join(FIXTURES_DIR, 'blog_result.json')
        with open(source_path, 'rb') as source_file:
            migration.import_data(source_file.read(), plan='create')

        migration = BlogCategoryMigration(BlogCategoryModel)
        source_path = os.path.join(FIXTURES_DIR, 'blog_category_result.json')
        with open(source_path, 'rb') as source_file:
            migration.import_data(source_file.read(), plan='direct')

    def test_all_fields(self):
        migration = QuerySetExportation(BlogCategoryModel.objects.all())
        self.assertEqual(
            [repr(fld) for fld in migration.fields],
            ['<yepes.data_migrations.fields.IntegerField: id>',
             '<yepes.data_migrations.fields.IntegerField: blog (blog_id)>',
             '<yepes.data_migrations.fields.TextField: name>',
             '<yepes.data_migrations.fields.TextField: description>'],
        )
        self.assertEqual(migration.fields_to_import, [])
        self.assertIsNone(migration.primary_key)
        self.assertIsNone(migration.natural_foreign_keys)
        self.assertFalse(migration.can_create)
        self.assertFalse(migration.can_update)
        self.assertFalse(migration.requires_model_instances)
        self.assertJSONEqual(
            migration.export_data(),
            """[
                {"id": 1, "blog": 1, "name": "Pets", "description": ""},
                {"id": 2, "blog": 1, "name": "Toys", "description": ""},
                {"id": 3, "blog": 3, "name": "Programming Languages", "description": ""},
                {"id": 4, "blog": 3, "name": "Development Tools", "description": ""},
                {"id": 5, "blog": 3, "name": "App Reviews", "description": ""},
                {"id": 6, "blog": 5, "name": "State Secrets", "description": "Political scandals and things like those."},
                {"id": 7, "blog": 5, "name": "Some Nonsense", "description": "This cannot be described."}
            ]""")

    def test_selected_fields(self):
        migration = QuerySetExportation(BlogCategoryModel.objects.only('id', 'name'))
        self.assertEqual(
            [repr(fld) for fld in migration.fields],
            ['<yepes.data_migrations.fields.IntegerField: id>',
             '<yepes.data_migrations.fields.TextField: name>'],
        )
        self.assertEqual(migration.fields_to_import, [])
        self.assertIsNone(migration.primary_key)
        self.assertIsNone(migration.natural_foreign_keys)
        self.assertFalse(migration.can_create)
        self.assertFalse(migration.can_update)
        self.assertFalse(migration.requires_model_instances)
        self.assertJSONEqual(
            migration.export_data(),
            """[
                {"id": 1, "name": "Pets"},
                {"id": 2, "name": "Toys"},
                {"id": 3, "name": "Programming Languages"},
                {"id": 4, "name": "Development Tools"},
                {"id": 5, "name": "App Reviews"},
                {"id": 6, "name": "State Secrets"},
                {"id": 7, "name": "Some Nonsense"}
            ]""")

    def test_excluded_fields(self):
        migration = QuerySetExportation(BlogCategoryModel.objects.defer('description'))
        self.assertEqual(
            [repr(fld) for fld in migration.fields],
            ['<yepes.data_migrations.fields.IntegerField: id>',
             '<yepes.data_migrations.fields.IntegerField: blog (blog_id)>',
             '<yepes.data_migrations.fields.TextField: name>'],
        )
        self.assertEqual(migration.fields_to_import, [])
        self.assertIsNone(migration.primary_key)
        self.assertIsNone(migration.natural_foreign_keys)
        self.assertFalse(migration.can_create)
        self.assertFalse(migration.can_update)
        self.assertFalse(migration.requires_model_instances)
        self.assertJSONEqual(
            migration.export_data(),
            """[
                {"id": 1, "blog": 1, "name": "Pets"},
                {"id": 2, "blog": 1, "name": "Toys"},
                {"id": 3, "blog": 3, "name": "Programming Languages"},
                {"id": 4, "blog": 3, "name": "Development Tools"},
                {"id": 5, "blog": 3, "name": "App Reviews"},
                {"id": 6, "blog": 5, "name": "State Secrets"},
                {"id": 7, "blog": 5, "name": "Some Nonsense"}
            ]""")

    def test_evaluated_queryset(self):
        qs = BlogCategoryModel.objects.all()
        len(qs)  # Evaluate queryset
        migration = QuerySetExportation(qs)
        self.assertEqual(
            [repr(fld) for fld in migration.fields],
            ['<yepes.data_migrations.fields.IntegerField: id>',
             '<yepes.data_migrations.fields.IntegerField: blog (blog_id)>',
             '<yepes.data_migrations.fields.TextField: name>',
             '<yepes.data_migrations.fields.TextField: description>'],
        )
        self.assertEqual(migration.fields_to_import, [])
        self.assertIsNone(migration.primary_key)
        self.assertIsNone(migration.natural_foreign_keys)
        self.assertFalse(migration.can_create)
        self.assertFalse(migration.can_update)
        self.assertTrue(migration.requires_model_instances)
        with self.assertNumQueries(0):  # Uses loaded objects
            self.assertJSONEqual(
                migration.export_data(),
                """[
                    {"id": 1, "blog": 1, "name": "Pets", "description": ""},
                    {"id": 2, "blog": 1, "name": "Toys", "description": ""},
                    {"id": 3, "blog": 3, "name": "Programming Languages", "description": ""},
                    {"id": 4, "blog": 3, "name": "Development Tools", "description": ""},
                    {"id": 5, "blog": 3, "name": "App Reviews", "description": ""},
                    {"id": 6, "blog": 5, "name": "State Secrets", "description": "Political scandals and things like those."},
                    {"id": 7, "blog": 5, "name": "Some Nonsense", "description": "This cannot be described."}
                ]""")

    def test_filtered_queryset(self):
        qs = BlogCategoryModel.objects.all()
        migration = QuerySetExportation(qs.filter(name__startswith='S'))
        self.assertEqual(
            [repr(fld) for fld in migration.fields],
            ['<yepes.data_migrations.fields.IntegerField: id>',
             '<yepes.data_migrations.fields.IntegerField: blog (blog_id)>',
             '<yepes.data_migrations.fields.TextField: name>',
             '<yepes.data_migrations.fields.TextField: description>'],
        )
        self.assertEqual(migration.fields_to_import, [])
        self.assertIsNone(migration.primary_key)
        self.assertIsNone(migration.natural_foreign_keys)
        self.assertFalse(migration.can_create)
        self.assertFalse(migration.can_update)
        self.assertFalse(migration.requires_model_instances)
        self.assertJSONEqual(
            migration.export_data(),
            """[
                {"id": 6, "blog": 5, "name": "State Secrets", "description": "Political scandals and things like those."},
                {"id": 7, "blog": 5, "name": "Some Nonsense", "description": "This cannot be described."}
            ]""")

    def test_sliced_queryset(self):
        qs = BlogCategoryModel.objects.all()
        migration = QuerySetExportation(qs[0:4])
        self.assertEqual(
            [repr(fld) for fld in migration.fields],
            ['<yepes.data_migrations.fields.IntegerField: id>',
             '<yepes.data_migrations.fields.IntegerField: blog (blog_id)>',
             '<yepes.data_migrations.fields.TextField: name>',
             '<yepes.data_migrations.fields.TextField: description>'],
        )
        self.assertEqual(migration.fields_to_import, [])
        self.assertIsNone(migration.primary_key)
        self.assertIsNone(migration.natural_foreign_keys)
        self.assertFalse(migration.can_create)
        self.assertFalse(migration.can_update)
        self.assertFalse(migration.requires_model_instances)
        self.assertJSONEqual(
            migration.export_data(),
            """[
                {"id": 1, "blog": 1, "name": "Pets", "description": ""},
                {"id": 2, "blog": 1, "name": "Toys", "description": ""},
                {"id": 3, "blog": 3, "name": "Programming Languages", "description": ""},
                {"id": 4, "blog": 3, "name": "Development Tools", "description": ""}
            ]""")

    def test_sorted_queryset(self):
        qs = BlogCategoryModel.objects.all()
        migration = QuerySetExportation(qs.order_by('name'))
        self.assertEqual(
            [repr(fld) for fld in migration.fields],
            ['<yepes.data_migrations.fields.IntegerField: id>',
             '<yepes.data_migrations.fields.IntegerField: blog (blog_id)>',
             '<yepes.data_migrations.fields.TextField: name>',
             '<yepes.data_migrations.fields.TextField: description>'],
        )
        self.assertEqual(migration.fields_to_import, [])
        self.assertIsNone(migration.primary_key)
        self.assertIsNone(migration.natural_foreign_keys)
        self.assertFalse(migration.can_create)
        self.assertFalse(migration.can_update)
        self.assertFalse(migration.requires_model_instances)
        self.assertJSONEqual(
            migration.export_data(),
            """[
                {"id": 5, "blog": 3, "name": "App Reviews", "description": ""},
                {"id": 4, "blog": 3, "name": "Development Tools", "description": ""},
                {"id": 1, "blog": 1, "name": "Pets", "description": ""},
                {"id": 3, "blog": 3, "name": "Programming Languages", "description": ""},
                {"id": 7, "blog": 5, "name": "Some Nonsense", "description": "This cannot be described."},
                {"id": 6, "blog": 5, "name": "State Secrets", "description": "Political scandals and things like those."},
                {"id": 2, "blog": 1, "name": "Toys", "description": ""}
            ]""")

