# -*- coding:utf-8 -*-

from __future__ import unicode_literals

import os

from django.test import TestCase
from django.utils._os import upath

from yepes.contrib.datamigrations import ModelMigration
from yepes.contrib.datamigrations.facades import (
    MultipleExportFacade,
    MultipleImportFacade,
    SingleExportFacade,
    SingleImportFacade,
)
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


class MultipleExportTest(TempDirMixin, TestCase):

    available_apps = ['datamigrations_facades']

    maxDiff = None
    tempDirPrefix = 'test_datamigrations_facades_'

    def test_no_file(self):
        with self.assertRaises(TypeError):
            MultipleExportFacade.to_file_path()

    def test_invalid_label(self):
        result_path = os.path.join(self.temp_dir, 'backup')
        with self.assertRaisesRegexp(LookupError, "No installed app with label 'appname_ModelName'."):
            MultipleExportFacade.to_file_path(result_path, models=['appname_ModelName'])

    def test_app_not_found(self):
        result_path = os.path.join(self.temp_dir, 'backup')
        with self.assertRaisesRegexp(LookupError, "No installed app with label 'appname'."):
            MultipleExportFacade.to_file_path(result_path, models=['appname.ModelName'])

    def test_model_not_found(self):
        result_path = os.path.join(self.temp_dir, 'backup')
        with self.assertRaisesRegexp(LookupError, "App 'datamigrations_facades_tests' doesn't have a '[Mm]odel[Nn]ame' model."):
            MultipleExportFacade.to_file_path(result_path, models=['datamigrations_facades_tests.ModelName'])

    def test_serializer_not_found(self):
        result_path = os.path.join(self.temp_dir, 'backup')
        with self.assertRaisesRegexp(LookupError, "Serializer 'serializername' could not be found."):
            MultipleExportFacade.to_file_path(result_path, models=['datamigrations_facades_tests.AlphabetModel'], serializer='serializername')

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
        MultipleExportFacade.to_file_path(
            result_path,
            serializer='json',
            use_natural_keys=True,
        )
        with open(source_path, 'r') as source_file:
            source = source_file.read()

        with open(result_path, 'r') as result_file:
            result = result_file.read()

        self.assertEqual(source.splitlines(), result.splitlines())

    def test_labels(self):
        migration = ModelMigration(CategoryModel)
        source_path = os.path.join(MIGRATIONS_DIR, 'category.json')
        with open(source_path, 'r') as source_file:
            migration.import_data(source_file, JsonSerializer, DirectPlan)

        result_path = os.path.join(self.temp_dir, 'backup')
        MultipleExportFacade.to_file_path(
            result_path,
            models=['datamigrations_facades_tests.CategoryModel'],
        )
        with open(result_path, 'r') as result_file:
            result = result_file.read()

        self.assertEqual(1, result.count('Type: MODEL;'))
        self.assertIn('Name: datamigrations_facades_tests.categorymodel;', result)


class MultipleImportTest(TempDirMixin, TestCase):

    available_apps = ['datamigrations_facades']

    maxDiff = None
    tempDirPrefix = 'test_datamigrations_facades_'

    def test_no_file(self):
        with self.assertRaises(TypeError):
            MultipleImportFacade.from_file_path()

    def test_file_not_found(self):
        with self.assertRaisesRegexp(AttributeError, "File 'filename' does not exit."):
            MultipleImportFacade.from_file_path('filename')

    def test_invalid_file(self):
        source_path = os.path.join(MIGRATIONS_DIR, 'alphabet.csv')
        with self.assertRaisesRegexp(ValueError, 'Invalid file format.'):
            MultipleImportFacade.from_file_path(source_path)

    def test_invalid_label(self):
        source_path = os.path.join(MIGRATIONS_DIR, 'backup')
        with self.assertRaisesRegexp(LookupError, "No installed app with label 'appname_ModelName'."):
            MultipleImportFacade.from_file_path(source_path, models=['appname_ModelName'])

    def test_app_not_found(self):
        source_path = os.path.join(MIGRATIONS_DIR, 'backup')
        with self.assertRaisesRegexp(LookupError, "No installed app with label 'appname'."):
            MultipleImportFacade.from_file_path(source_path, models=['appname.ModelName'])

    def test_model_not_found(self):
        source_path = os.path.join(MIGRATIONS_DIR, 'backup')
        with self.assertRaisesRegexp(LookupError, "App 'datamigrations_facades_tests' doesn't have a '[Mm]odel[Nn]ame' model."):
            MultipleImportFacade.from_file_path(source_path, models=['datamigrations_facades_tests.ModelName'])

    def test_serializer_not_found(self):
        source_path = os.path.join(MIGRATIONS_DIR, 'backup')
        with self.assertRaisesRegexp(LookupError, "Serializer 'serializername' could not be found."):
            MultipleImportFacade.from_file_path(source_path, models=['datamigrations_facades_tests.AlphabetModel'], serializer='serializername')

    def test_importation_plan_not_found(self):
        source_path = os.path.join(MIGRATIONS_DIR, 'backup')
        with self.assertRaisesRegexp(LookupError, "Importation plan 'planname' could not be found."):
            MultipleImportFacade.from_file_path(source_path, models=['datamigrations_facades_tests.AlphabetModel'], plan='planname')

    def test_file(self):
        source_path = os.path.join(MIGRATIONS_DIR, 'backup')
        MultipleImportFacade.from_file_path(
            source_path,
            use_natural_keys=True,
            plan='direct',
        )
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
        MultipleImportFacade.from_file_path(
            source_path,
            models=[
                'datamigrations_facades_tests.AuthorModel',
                'datamigrations_facades_tests.CategoryModel',
            ],
            plan='direct',
            use_natural_keys=True,
        )
        self.assertEqual(3, AuthorModel.objects.count())
        self.assertEqual(2, CategoryModel.objects.count())
        self.assertEqual(0, PostModel.objects.count())

    def test_serializer(self):
        source_path = os.path.join(MIGRATIONS_DIR, 'backup')
        with self.assertRaises(Exception):
            MultipleImportFacade.from_file_path(
                source_path,
                serializer='csv',
                plan='direct',
                use_natural_keys=True,
            )


class SingleExportTest(TempDirMixin, TestCase):

    available_apps = ['datamigrations_facades']

    maxDiff = None
    tempDirPrefix = 'test_datamigrations_facades_'

    def test_no_file(self):
        with self.assertRaises(TypeError):
            SingleExportFacade.to_file_path()

    def test_no_label(self):
        result_path = os.path.join(self.temp_dir, 'alphabet.csv')
        with self.assertRaisesRegexp(AttributeError, 'You must give a model.'):
            SingleExportFacade.to_file_path(result_path)

    def test_invalid_label(self):
        result_path = os.path.join(self.temp_dir, 'alphabet.csv')
        with self.assertRaises(ValueError):
            SingleExportFacade.to_file_path(result_path, model='appname_ModelName')

    def test_app_not_found(self):
        result_path = os.path.join(self.temp_dir, 'alphabet.csv')
        with self.assertRaisesRegexp(LookupError, "No installed app with label 'appname'."):
            SingleExportFacade.to_file_path(result_path, model='appname.ModelName')

    def test_model_not_found(self):
        result_path = os.path.join(self.temp_dir, 'alphabet.csv')
        with self.assertRaisesRegexp(LookupError, "App 'datamigrations_facades_tests' doesn't have a '[Mm]odel[Nn]ame' model."):
            SingleExportFacade.to_file_path(result_path, model='datamigrations_facades_tests.ModelName')

    def test_serializer_not_found(self):
        result_path = os.path.join(self.temp_dir, 'alphabet.csv')
        with self.assertRaisesRegexp(LookupError, "Serializer 'serializername' could not be found."):
            SingleExportFacade.to_file_path(result_path, model='datamigrations_facades_tests.AlphabetModel', serializer='serializername')

    def test_file(self):
        migration = ModelMigration(AlphabetModel)
        source_path = os.path.join(MIGRATIONS_DIR, 'alphabet.csv')
        result_path = os.path.join(self.temp_dir, 'alphabet.csv')
        with open(source_path, 'r') as source_file:
            source = source_file.read()

        migration.import_data(source, CsvSerializer, DirectPlan)
        SingleExportFacade.to_file_path(
            result_path,
            model='datamigrations_facades_tests.AlphabetModel',
            serializer='csv',
        )
        with open(result_path, 'r') as result_file:
            result = result_file.read()

        self.assertEqual(source.splitlines(), result.splitlines())


class SingleImportTest(TempDirMixin, TestCase):

    available_apps = ['datamigrations_facades']

    maxDiff = None
    tempDirPrefix = 'test_datamigrations_facades_'

    def test_no_file(self):
        with self.assertRaises(TypeError):
            SingleImportFacade.from_file_path()

    def test_file_not_found(self):
        with self.assertRaisesRegexp(AttributeError, "File 'filename' does not exit."):
            SingleImportFacade.from_file_path('filename')

    def test_no_label(self):
        source_path = os.path.join(MIGRATIONS_DIR, 'alphabet.csv')
        with self.assertRaisesRegexp(AttributeError, 'You must give a model.'):
            SingleImportFacade.from_file_path(source_path)

    def test_invalid_label(self):
        source_path = os.path.join(MIGRATIONS_DIR, 'alphabet.csv')
        with self.assertRaises(ValueError):
            SingleImportFacade.from_file_path(source_path, model='appname_ModelName')

    def test_app_not_found(self):
        source_path = os.path.join(MIGRATIONS_DIR, 'alphabet.csv')
        with self.assertRaisesRegexp(LookupError, "No installed app with label 'appname'."):
            SingleImportFacade.from_file_path(source_path, model='appname.ModelName')

    def test_model_not_found(self):
        source_path = os.path.join(MIGRATIONS_DIR, 'alphabet.csv')
        with self.assertRaisesRegexp(LookupError, "App 'datamigrations_facades_tests' doesn't have a '[Mm]odel[Nn]ame' model."):
            SingleImportFacade.from_file_path(source_path, model='datamigrations_facades_tests.ModelName')

    def test_serializer_not_found(self):
        source_path = os.path.join(MIGRATIONS_DIR, 'alphabet.csv')
        with self.assertRaisesRegexp(LookupError, "Serializer 'serializername' could not be found."):
            SingleImportFacade.from_file_path(source_path, model='datamigrations_facades_tests.AlphabetModel', serializer='serializername')

    def test_importation_plan_not_found(self):
        source_path = os.path.join(MIGRATIONS_DIR, 'alphabet.csv')
        with self.assertRaisesRegexp(LookupError, "Importation plan 'planname' could not be found."):
            SingleImportFacade.from_file_path(source_path, model='datamigrations_facades_tests.AlphabetModel', plan='planname')

    def test_file(self):
        migration = ModelMigration(AlphabetModel)
        source_path = os.path.join(MIGRATIONS_DIR, 'alphabet.csv')
        with open(source_path, 'r') as source_file:
            source = source_file.read()

        SingleImportFacade.from_file_path(
            source_path,
            model='datamigrations_facades_tests.AlphabetModel',
            serializer='csv',
        )
        result = migration.export_data(serializer=CsvSerializer)
        self.assertEqual(source.splitlines(), result.splitlines())

