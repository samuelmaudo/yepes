# -*- coding:utf-8 -*-

from __future__ import unicode_literals

import os

from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase
from django.utils._os import upath
from django.utils.six import StringIO

from yepes.apps.data_migrations import DataMigration
from yepes.apps.data_migrations.importation_plans.direct import DirectPlan
from yepes.apps.data_migrations.serializers.csv import CsvSerializer
from yepes.test_mixins import TempDirMixin

from .models import AlphabetModel

MODULE_DIR = os.path.abspath(os.path.dirname(upath(__file__)))
FIXTURES_DIR = os.path.join(MODULE_DIR, 'data_migrations')


class ExportModelTest(TempDirMixin, TestCase):

    maxDiff = None
    tempDirPrefix = 'test_datamigrations_commands_'

    def test_no_label(self):
        with self.assertRaisesRegexp(CommandError, 'This command takes one and only one positional argument.'):
            call_command('export_model')

    def test_invalid_label(self):
        with self.assertRaisesRegexp(CommandError, "Model label must be like 'appname.ModelName'."):
            call_command('export_model', 'appname_ModelName')

    def test_multiple_labels(self):
        with self.assertRaisesRegexp(CommandError, 'This command takes one and only one positional argument.'):
            call_command('export_model', 'appname.ModelName', 'appname.ModelName')

    def test_app_not_found(self):
        with self.assertRaisesRegexp(CommandError, "App with label 'appname' could not be found."):
            call_command('export_model', 'appname.ModelName')

    def test_model_not_found(self):
        with self.assertRaisesRegexp(CommandError, "Model 'ModelName' could not be found."):
            call_command('export_model', 'datamigrations_commands.ModelName')

    def test_serializer_not_found(self):
        with self.assertRaisesRegexp(CommandError, "Serializer 'serializername' could not be found."):
            call_command('export_model', 'datamigrations_commands.AlphabetModel', format='serializername')

    def test_no_file(self):
        migration = DataMigration(AlphabetModel)
        source_path = os.path.join(FIXTURES_DIR, 'alphabet.csv')
        with open(source_path, 'r') as source_file:
            source = source_file.read()

        migration.import_data(source, CsvSerializer, DirectPlan)
        output = StringIO()
        call_command(
            'export_model',
            'datamigrations_commands.AlphabetModel',
            format='csv',
            stdout=output,
        )
        result = output.getvalue()
        self.assertEqual(source.splitlines(), result.splitlines())

    def test_file(self):
        migration = DataMigration(AlphabetModel)
        source_path = os.path.join(FIXTURES_DIR, 'alphabet.csv')
        result_path = os.path.join(self.temp_dir, 'alphabet.csv')
        with open(source_path, 'r') as source_file:
            source = source_file.read()

        migration.import_data(source, CsvSerializer, DirectPlan)
        output = StringIO()
        call_command(
            'export_model',
            'datamigrations_commands.AlphabetModel',
            format='csv',
            output=result_path,
            stdout=output,
        )
        with open(result_path, 'r') as result_file:
            result = result_file.read()

        self.assertEqual(source.splitlines(), result.splitlines())
        self.assertIn('Objects were successfully exported.', output.getvalue())


class ImportModelTest(TempDirMixin, TestCase):

    maxDiff = None
    tempDirPrefix = 'test_datamigrations_commands_'

    def test_no_label(self):
        with self.assertRaisesRegexp(CommandError, 'This command takes one and only one positional argument.'):
            call_command('import_model')

    def test_invalid_label(self):
        with self.assertRaisesRegexp(CommandError, "Model label must be like 'appname.ModelName'."):
            call_command('import_model', 'appname_ModelName')

    def test_multiple_labels(self):
        with self.assertRaisesRegexp(CommandError, 'This command takes one and only one positional argument.'):
            call_command('import_model', 'appname.ModelName', 'appname.ModelName')

    def test_no_file(self):
        with self.assertRaisesRegexp(CommandError, 'You must give an input file.'):
            call_command('import_model', 'appname.ModelName')

    def test_file_not_found(self):
        with self.assertRaisesRegexp(CommandError, "File 'filename' does not exit."):
            call_command('import_model', 'appname.ModelName', input='filename')

    def test_app_not_found(self):
        source_path = os.path.join(FIXTURES_DIR, 'alphabet.csv')
        with self.assertRaisesRegexp(CommandError, "App with label 'appname' could not be found."):
            call_command('import_model', 'appname.ModelName', input=source_path)

    def test_model_not_found(self):
        source_path = os.path.join(FIXTURES_DIR, 'alphabet.csv')
        with self.assertRaisesRegexp(CommandError, "Model 'ModelName' could not be found."):
            call_command('import_model', 'datamigrations_commands.ModelName', input=source_path)

    def test_serializer_not_found(self):
        source_path = os.path.join(FIXTURES_DIR, 'alphabet.csv')
        with self.assertRaisesRegexp(CommandError, "Serializer 'serializername' could not be found."):
            call_command('import_model', 'datamigrations_commands.AlphabetModel', input=source_path, format='serializername')

    def test_importation_plan_not_found(self):
        source_path = os.path.join(FIXTURES_DIR, 'alphabet.csv')
        with self.assertRaisesRegexp(CommandError, "Importation plan 'planname' could not be found."):
            call_command('import_model', 'datamigrations_commands.AlphabetModel', input=source_path, plan='planname')

    def test_file(self):
        migration = DataMigration(AlphabetModel)
        source_path = os.path.join(FIXTURES_DIR, 'alphabet.csv')
        with open(source_path, 'r') as source_file:
            source = source_file.read()

        output = StringIO()
        call_command(
            'import_model',
            'datamigrations_commands.AlphabetModel',
            format='csv',
            input=source_path,
            stdout=output,
        )
        result = migration.export_data(serializer=CsvSerializer)

        self.assertEqual(source.splitlines(), result.splitlines())
        self.assertIn('Entries were successfully imported.', output.getvalue())

