# -*- coding:utf-8 -*-

from __future__ import unicode_literals

import os
from unittest import expectedFailure

from django.core.management import call_command, CommandError
from django.test import TestCase
from django.utils._os import upath
from django.utils.six import StringIO

from yepes.contrib.datamigrations import ModelMigration
from yepes.contrib.datamigrations.importation_plans.direct import DirectPlan
from yepes.contrib.datamigrations.serializers.csv import CsvSerializer
from yepes.contrib.datamigrations.serializers.json import JsonSerializer
from yepes.test_mixins import TempDirMixin

from .models import (
    AlphabetModel,
    AuthorModel,
    CategoryModel,
    PostModel,
)

MODULE_DIR = os.path.abspath(os.path.dirname(upath(__file__)))
MIGRATIONS_DIR = os.path.join(MODULE_DIR, 'data_migrations')


class ExportModelTest(TempDirMixin, TestCase):

    available_apps = ['yepes.contrib.datamigrations', 'datamigrations_commands']

    maxDiff = None
    tempDirPrefix = 'test_datamigrations_commands_'

    def test_no_label(self):
        with self.assertRaisesRegexp(CommandError, 'You must give a model.'):
            call_command('export_model')

    def test_invalid_label(self):
        with self.assertRaisesRegexp(CommandError, "Model label must be like 'appname.ModelName'."):
            call_command('export_model', 'appname_ModelName')

    def test_multiple_labels(self):
        with self.assertRaisesRegexp(CommandError, 'This command takes only one positional argument.'):
            call_command('export_model', 'appname.ModelName', 'appname.ModelName')

    def test_app_not_found(self):
        with self.assertRaisesRegexp(CommandError, "No installed app with label 'appname'."):
            call_command('export_model', 'appname.ModelName')

    def test_model_not_found(self):
        with self.assertRaisesRegexp(CommandError, "App 'datamigrations_commands_tests' doesn't have a '[Mm]odel[Nn]ame' model."):
            call_command('export_model', 'datamigrations_commands_tests.ModelName')

    def test_serializer_not_found(self):
        with self.assertRaisesRegexp(CommandError, "Serializer 'serializername' could not be found."):
            call_command('export_model', 'datamigrations_commands_tests.AlphabetModel', format='serializername')

    def test_no_file(self):
        migration = ModelMigration(AlphabetModel)
        source_path = os.path.join(MIGRATIONS_DIR, 'alphabet.csv')
        with open(source_path, 'r') as source_file:
            source = source_file.read()

        migration.import_data(source, CsvSerializer, DirectPlan)
        output = StringIO()
        call_command(
            'export_model',
            'datamigrations_commands_tests.AlphabetModel',
            format='csv',
            stdout=output,
        )
        result = output.getvalue()
        self.assertEqual(source.splitlines(), result.splitlines())

    def test_file(self):
        migration = ModelMigration(AlphabetModel)
        source_path = os.path.join(MIGRATIONS_DIR, 'alphabet.csv')
        result_path = os.path.join(self.temp_dir, 'alphabet.csv')
        with open(source_path, 'r') as source_file:
            source = source_file.read()

        migration.import_data(source, CsvSerializer, DirectPlan)
        output = StringIO()
        call_command(
            'export_model',
            'datamigrations_commands_tests.AlphabetModel',
            file=result_path,
            format='csv',
            stdout=output,
        )
        with open(result_path, 'r') as result_file:
            result = result_file.read()

        self.assertEqual(source.splitlines(), result.splitlines())
        self.assertIn('Objects were successfully exported.', output.getvalue())


class ExportModelsTest(TempDirMixin, TestCase):

    available_apps = ['yepes.contrib.datamigrations', 'datamigrations_commands']

    maxDiff = None
    tempDirPrefix = 'test_datamigrations_commands_'

    def test_invalid_label(self):
        with self.assertRaisesRegexp(CommandError, "No installed app with label 'appname_ModelName'."):
            call_command('export_models', 'appname_ModelName')

    def test_app_not_found(self):
        with self.assertRaisesRegexp(CommandError, "No installed app with label 'appname'."):
            call_command('export_models', 'appname.ModelName')

    def test_model_not_found(self):
        with self.assertRaisesRegexp(CommandError, "App 'datamigrations_commands_tests' doesn't have a '[Mm]odel[Nn]ame' model."):
            call_command('export_models', 'datamigrations_commands_tests.ModelName')

    def test_serializer_not_found(self):
        with self.assertRaisesRegexp(CommandError, "Serializer 'serializername' could not be found."):
            call_command('export_models', 'datamigrations_commands_tests.AlphabetModel', format='serializername')

    @expectedFailure
    def test_no_file(self):
        migration = ModelMigration(AuthorModel)
        source_path = os.path.join(MIGRATIONS_DIR, 'author.json')
        with open(source_path, 'r') as source_file:
            migration.import_data(source_file, JsonSerializer, DirectPlan)

        migration = ModelMigration(CategoryModel)
        source_path = os.path.join(MIGRATIONS_DIR, 'category.json')
        with open(source_path, 'r') as source_file:
            migration.import_data(source_file, JsonSerializer, DirectPlan)

        migration = ModelMigration(PostModel)
        source_path = os.path.join(MIGRATIONS_DIR, 'post.json')
        with open(source_path, 'r') as source_file:
            migration.import_data(source_file, JsonSerializer, DirectPlan)

        source_path = os.path.join(MIGRATIONS_DIR, 'backup')
        output = StringIO()
        call_command(
            'export_models',
            format='json',
            natural=True,
            stdout=output,
        )
        with open(source_path, 'r') as source_file:
            source = source_file.read()

        result = output.getvalue()
        self.assertEqual(source.splitlines(), result.splitlines())

    def test_file(self):
        migration = ModelMigration(AuthorModel)
        source_path = os.path.join(MIGRATIONS_DIR, 'author.json')
        with open(source_path, 'r') as source_file:
            migration.import_data(source_file, JsonSerializer, DirectPlan)

        migration = ModelMigration(CategoryModel)
        source_path = os.path.join(MIGRATIONS_DIR, 'category.json')
        with open(source_path, 'r') as source_file:
            migration.import_data(source_file, JsonSerializer, DirectPlan)

        migration = ModelMigration(PostModel)
        source_path = os.path.join(MIGRATIONS_DIR, 'post.json')
        with open(source_path, 'r') as source_file:
            migration.import_data(source_file, JsonSerializer, DirectPlan)

        source_path = os.path.join(MIGRATIONS_DIR, 'backup')
        result_path = os.path.join(self.temp_dir, 'backup')
        output = StringIO()
        call_command(
            'export_models',
            file=result_path,
            format='json',
            natural=True,
            stdout=output,
        )
        with open(source_path, 'r') as source_file:
            source = source_file.read()

        with open(result_path, 'r') as result_file:
            result = result_file.read()

        self.assertEqual(source.splitlines(), result.splitlines())
        self.assertIn('Objects were successfully exported.', output.getvalue())

    def test_labels(self):
        migration = ModelMigration(CategoryModel)
        source_path = os.path.join(MIGRATIONS_DIR, 'category.json')
        with open(source_path, 'r') as source_file:
            migration.import_data(source_file, JsonSerializer, DirectPlan)

        result_path = os.path.join(self.temp_dir, 'backup')
        output = StringIO()
        call_command(
            'export_models',
            'datamigrations_commands_tests.CategoryModel',
            file=result_path,
            format='json',
            natural=True,
            stdout=output,
        )
        with open(result_path, 'r') as result_file:
            result = result_file.read()

        self.assertEqual(1, result.count('Type: MODEL;'))
        self.assertIn('Name: datamigrations_commands_tests.categorymodel;', result)


class ImportModelTest(TempDirMixin, TestCase):

    available_apps = ['yepes.contrib.datamigrations', 'datamigrations_commands']

    maxDiff = None
    tempDirPrefix = 'test_datamigrations_commands_'

    def test_no_file(self):
        with self.assertRaisesRegexp(CommandError, 'You must give an input file.'):
            call_command('import_model')

    def test_file_not_found(self):
        with self.assertRaisesRegexp(CommandError, "File 'filename' does not exit."):
            call_command('import_model', file='filename')

    def test_no_label(self):
        source_path = os.path.join(MIGRATIONS_DIR, 'alphabet.csv')
        with self.assertRaisesRegexp(CommandError, 'You must give a model.'):
            call_command('import_model', file=source_path)

    def test_invalid_label(self):
        source_path = os.path.join(MIGRATIONS_DIR, 'alphabet.csv')
        with self.assertRaisesRegexp(CommandError, "Model label must be like 'appname.ModelName'."):
            call_command('import_model', 'appname_ModelName', file=source_path)

    def test_multiple_labels(self):
        source_path = os.path.join(MIGRATIONS_DIR, 'alphabet.csv')
        with self.assertRaisesRegexp(CommandError, 'This command takes only one positional argument.'):
            call_command('import_model', 'appname.ModelName', 'appname.ModelName', file=source_path)

    def test_app_not_found(self):
        source_path = os.path.join(MIGRATIONS_DIR, 'alphabet.csv')
        with self.assertRaisesRegexp(CommandError, "No installed app with label 'appname'."):
            call_command('import_model', 'appname.ModelName', file=source_path)

    def test_model_not_found(self):
        source_path = os.path.join(MIGRATIONS_DIR, 'alphabet.csv')
        with self.assertRaisesRegexp(CommandError, "App 'datamigrations_commands_tests' doesn't have a '[Mm]odel[Nn]ame' model."):
            call_command('import_model', 'datamigrations_commands_tests.ModelName', file=source_path)

    def test_serializer_not_found(self):
        source_path = os.path.join(MIGRATIONS_DIR, 'alphabet.csv')
        with self.assertRaisesRegexp(CommandError, "Serializer 'serializername' could not be found."):
            call_command('import_model', 'datamigrations_commands_tests.AlphabetModel', file=source_path, format='serializername')

    def test_importation_plan_not_found(self):
        source_path = os.path.join(MIGRATIONS_DIR, 'alphabet.csv')
        with self.assertRaisesRegexp(CommandError, "Importation plan 'planname' could not be found."):
            call_command('import_model', 'datamigrations_commands_tests.AlphabetModel', file=source_path, plan='planname')

    def test_file(self):
        migration = ModelMigration(AlphabetModel)
        source_path = os.path.join(MIGRATIONS_DIR, 'alphabet.csv')
        with open(source_path, 'r') as source_file:
            source = source_file.read()

        output = StringIO()
        call_command(
            'import_model',
            'datamigrations_commands_tests.AlphabetModel',
            file=source_path,
            format='csv',
            stdout=output,
        )
        result = migration.export_data(serializer=CsvSerializer)

        self.assertEqual(source.splitlines(), result.splitlines())
        self.assertIn('Entries were successfully imported.', output.getvalue())


class ImportModelsTest(TempDirMixin, TestCase):

    available_apps = ['yepes.contrib.datamigrations', 'datamigrations_commands']

    maxDiff = None
    tempDirPrefix = 'test_datamigrations_commands_'

    def test_no_file(self):
        with self.assertRaisesRegexp(CommandError, 'You must give either an input file or a directory.'):
            call_command('import_models')

    def test_file_not_found(self):
        with self.assertRaisesRegexp(CommandError, "File 'filename' does not exit."):
            call_command('import_models', file='filename')

    def test_directory_not_found(self):
        with self.assertRaisesRegexp(CommandError, "Directory 'dirname' does not exit."):
            call_command('import_models', directory='dirname')

    def test_invalid_file(self):
        source_path = os.path.join(MIGRATIONS_DIR, 'alphabet.csv')
        with self.assertRaisesRegexp(CommandError, "Invalid file format."):
            call_command('import_models', file=source_path)

    def test_invalid_label(self):
        source_path = os.path.join(MIGRATIONS_DIR, 'backup')
        with self.assertRaisesRegexp(CommandError, "No installed app with label 'appname_ModelName'."):
            call_command('import_models', 'appname_ModelName', file=source_path)

    def test_app_not_found(self):
        source_path = os.path.join(MIGRATIONS_DIR, 'backup')
        with self.assertRaisesRegexp(CommandError, "No installed app with label 'appname'."):
            call_command('import_models', 'appname.ModelName', file=source_path)

    def test_model_not_found(self):
        source_path = os.path.join(MIGRATIONS_DIR, 'backup')
        with self.assertRaisesRegexp(CommandError, "App 'datamigrations_commands_tests' doesn't have a '[Mm]odel[Nn]ame' model."):
            call_command('import_models', 'datamigrations_commands_tests.ModelName', file=source_path)

    def test_serializer_not_found(self):
        source_path = os.path.join(MIGRATIONS_DIR, 'backup')
        with self.assertRaisesRegexp(CommandError, "Serializer 'serializername' could not be found."):
            call_command('import_models', file=source_path, format='serializername')

    def test_importation_plan_not_found(self):
        source_path = os.path.join(MIGRATIONS_DIR, 'backup')
        with self.assertRaisesRegexp(CommandError, "Importation plan 'planname' could not be found."):
            call_command('import_models', file=source_path, plan='planname')

    def test_file(self):
        source_path = os.path.join(MIGRATIONS_DIR, 'backup')
        output = StringIO()
        call_command(
            'import_models',
            file=source_path,
            plan='direct',
            natural=True,
            stdout=output,
        )
        self.assertIn('Entries were successfully imported.', output.getvalue())

        source_path = os.path.join(MIGRATIONS_DIR, 'author.json')
        with open(source_path, 'r') as source_file:
            source = source_file.read()

        migration = ModelMigration(AuthorModel)
        result = migration.export_data(None, JsonSerializer)
        self.assertEqual(source.splitlines(), result.splitlines())

        source_path = os.path.join(MIGRATIONS_DIR, 'category.json')
        with open(source_path, 'r') as source_file:
            source = source_file.read()

        migration = ModelMigration(CategoryModel)
        result = migration.export_data(None, JsonSerializer)
        self.assertEqual(source.splitlines(), result.splitlines())

        source_path = os.path.join(MIGRATIONS_DIR, 'post.json')
        with open(source_path, 'r') as source_file:
            source = source_file.read()

        migration = ModelMigration(PostModel)
        result = migration.export_data(None, JsonSerializer)
        self.assertEqual(source.splitlines(), result.splitlines())

    def test_labels(self):
        source_path = os.path.join(MIGRATIONS_DIR, 'backup')
        output = StringIO()
        call_command(
            'import_models',
            'datamigrations_commands_tests.AuthorModel',
            'datamigrations_commands_tests.CategoryModel',
            file=source_path,
            plan='direct',
            natural=True,
            stdout=output,
        )
        self.assertIn('Entries were successfully imported.', output.getvalue())

        self.assertEqual(3, AuthorModel.objects.count())
        self.assertEqual(2, CategoryModel.objects.count())
        self.assertEqual(0, PostModel.objects.count())

    def test_serializer(self):
        source_path = os.path.join(MIGRATIONS_DIR, 'backup')
        output = StringIO()
        with self.assertRaises(CommandError):
            call_command(
                'import_models',
                file=source_path,
                format='csv',
                plan='direct',
                natural=True,
                stdout=output,
            )

