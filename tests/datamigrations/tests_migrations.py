# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from io import open
import os

from django import test
from django.utils._os import upath

from yepes.contrib.datamigrations import (
    DataMigration,
    BaseModelMigration,
    ModelMigration,
    QuerySetExportation,
)
from yepes.contrib.datamigrations.exceptions import (
    UnableToCreateError,
    UnableToExportError,
    UnableToImportError,
    UnableToUpdateError,
)
from yepes.test_mixins import TempDirMixin

from .data_migrations import (
    BlogMigration,
    BlogCategoryMigration,
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
MIGRATIONS_DIR = os.path.join(MODULE_DIR, 'data_migrations')


class ModelMigrationsTests(test.TestCase):

    maxDiff = None

    def test_alphabet_model(self):
        migration = ModelMigration(AlphabetModel)
        self.assertEqual(
            [repr(fld) for fld in migration.fields],
            ['<yepes.contrib.datamigrations.fields.IntegerField: id>',
             '<yepes.contrib.datamigrations.fields.TextField: letter>',
             '<yepes.contrib.datamigrations.fields.TextField: word>'],
        )
        self.assertEqual(migration.fields_to_export, migration.fields)
        self.assertEqual(migration.fields_to_import, migration.fields)
        self.assertEqual(
            repr(migration.primary_key),
            '<yepes.contrib.datamigrations.fields.IntegerField: id>',
        )
        self.assertIsNone(migration.natural_foreign_keys)
        self.assertTrue(migration.can_create)
        self.assertTrue(migration.can_export)
        self.assertTrue(migration.can_import)
        self.assertTrue(migration.can_update)
        self.assertFalse(migration.requires_model_instances)

        migration = ModelMigration(
            AlphabetModel,
            use_natural_primary_keys=True,
            use_natural_foreign_keys=True,
        )
        self.assertEqual(
            [repr(fld) for fld in migration.fields],
            ['<yepes.contrib.datamigrations.fields.TextField: letter>',
             '<yepes.contrib.datamigrations.fields.TextField: word>'],
        )
        self.assertEqual(migration.fields_to_export, migration.fields)
        self.assertEqual(migration.fields_to_import, migration.fields)
        self.assertEqual(
            repr(migration.primary_key),
            '<yepes.contrib.datamigrations.fields.TextField: letter>',
        )
        self.assertIsNone(migration.natural_foreign_keys)
        self.assertTrue(migration.can_create)
        self.assertTrue(migration.can_export)
        self.assertTrue(migration.can_import)
        self.assertTrue(migration.can_update)
        self.assertFalse(migration.requires_model_instances)

    def test_author_model(self):
        migration = ModelMigration(AuthorModel)
        self.assertEqual(
            [repr(fld) for fld in migration.fields],
            ['<yepes.contrib.datamigrations.fields.IntegerField: id>',
             '<yepes.contrib.datamigrations.fields.TextField: name>',
             '<yepes.contrib.datamigrations.fields.FileField: image>'],
        )
        self.assertEqual(migration.fields_to_export, migration.fields)
        self.assertEqual(migration.fields_to_import, migration.fields)
        self.assertEqual(
            repr(migration.primary_key),
            '<yepes.contrib.datamigrations.fields.IntegerField: id>',
        )
        self.assertIsNone(migration.natural_foreign_keys)
        self.assertTrue(migration.can_create)
        self.assertTrue(migration.can_export)
        self.assertTrue(migration.can_import)
        self.assertTrue(migration.can_update)
        self.assertFalse(migration.requires_model_instances)

        migration = ModelMigration(
            AuthorModel,
            use_natural_primary_keys=True,
            use_natural_foreign_keys=True,
        )
        self.assertEqual(
            [repr(fld) for fld in migration.fields],
            ['<yepes.contrib.datamigrations.fields.TextField: name>',
             '<yepes.contrib.datamigrations.fields.FileField: image>'],
        )
        self.assertEqual(migration.fields_to_export, migration.fields)
        self.assertEqual(migration.fields_to_import, migration.fields)
        self.assertEqual(
            repr(migration.primary_key),
            '<yepes.contrib.datamigrations.fields.TextField: name>',
        )
        self.assertIsNone(migration.natural_foreign_keys)
        self.assertTrue(migration.can_create)
        self.assertTrue(migration.can_export)
        self.assertTrue(migration.can_import)
        self.assertTrue(migration.can_update)
        self.assertFalse(migration.requires_model_instances)

    def test_blog_model(self):
        migration = ModelMigration(BlogModel)
        self.assertEqual(
            [repr(fld) for fld in migration.fields],
            ['<yepes.contrib.datamigrations.fields.IntegerField: id>',
             '<yepes.contrib.datamigrations.fields.TextField: name>',
             '<yepes.contrib.datamigrations.fields.TextField: description>'],
        )
        self.assertEqual(migration.fields_to_export, migration.fields)
        self.assertEqual(migration.fields_to_import, migration.fields)
        self.assertEqual(
            repr(migration.primary_key),
            '<yepes.contrib.datamigrations.fields.IntegerField: id>',
        )
        self.assertIsNone(migration.natural_foreign_keys)
        self.assertTrue(migration.can_create)
        self.assertTrue(migration.can_export)
        self.assertTrue(migration.can_import)
        self.assertTrue(migration.can_update)
        self.assertFalse(migration.requires_model_instances)

        migration = ModelMigration(
            BlogModel,
            use_natural_primary_keys=True,
            use_natural_foreign_keys=True,
        )
        self.assertEqual(
            [repr(fld) for fld in migration.fields],
            ['<yepes.contrib.datamigrations.fields.TextField: name>',
             '<yepes.contrib.datamigrations.fields.TextField: description>'],
        )
        self.assertEqual(migration.fields_to_export, migration.fields)
        self.assertEqual(migration.fields_to_import, migration.fields)
        self.assertEqual(
            repr(migration.primary_key),
            '<yepes.contrib.datamigrations.fields.TextField: name>',
        )
        self.assertIsNone(migration.natural_foreign_keys)
        self.assertTrue(migration.can_create)
        self.assertTrue(migration.can_export)
        self.assertTrue(migration.can_import)
        self.assertTrue(migration.can_update)
        self.assertFalse(migration.requires_model_instances)

    def test_blog_category_model(self):
        migration = ModelMigration(BlogCategoryModel)
        self.assertEqual(
            [repr(fld) for fld in migration.fields],
            ['<yepes.contrib.datamigrations.fields.IntegerField: id>',
             '<yepes.contrib.datamigrations.fields.IntegerField: blog (blog_id)>',
             '<yepes.contrib.datamigrations.fields.TextField: name>',
             '<yepes.contrib.datamigrations.fields.TextField: description>'],
        )
        self.assertEqual(migration.fields_to_export, migration.fields)
        self.assertEqual(migration.fields_to_import, migration.fields)
        self.assertEqual(
            repr(migration.primary_key),
            '<yepes.contrib.datamigrations.fields.IntegerField: id>',
        )
        self.assertIsNone(migration.natural_foreign_keys)
        self.assertTrue(migration.can_create)
        self.assertTrue(migration.can_export)
        self.assertTrue(migration.can_import)
        self.assertTrue(migration.can_update)
        self.assertFalse(migration.requires_model_instances)

    def test_boolean_migration(self):
        migration = ModelMigration(BooleanModel)
        self.assertEqual(
            [repr(fld) for fld in migration.fields],
            ['<yepes.contrib.datamigrations.fields.IntegerField: id>',
             '<yepes.contrib.datamigrations.fields.BooleanField: boolean>',
             '<yepes.contrib.datamigrations.fields.BooleanField: boolean_as_string>',
             '<yepes.contrib.datamigrations.fields.BooleanField: null_boolean>',
             '<yepes.contrib.datamigrations.fields.BooleanField: null_boolean_as_string>'],
        )
        self.assertEqual(migration.fields_to_export, migration.fields)
        self.assertEqual(migration.fields_to_import, migration.fields)
        self.assertEqual(
            repr(migration.primary_key),
            '<yepes.contrib.datamigrations.fields.IntegerField: id>',
        )
        self.assertIsNone(migration.natural_foreign_keys)
        self.assertTrue(migration.can_create)
        self.assertTrue(migration.can_export)
        self.assertTrue(migration.can_import)
        self.assertTrue(migration.can_update)
        self.assertFalse(migration.requires_model_instances)

        migration = ModelMigration(
            BooleanModel,
            use_natural_primary_keys=True,
            use_natural_foreign_keys=True,
        )
        self.assertEqual(
            [repr(fld) for fld in migration.fields],
            ['<yepes.contrib.datamigrations.fields.IntegerField: id>',
             '<yepes.contrib.datamigrations.fields.BooleanField: boolean>',
             '<yepes.contrib.datamigrations.fields.BooleanField: boolean_as_string>',
             '<yepes.contrib.datamigrations.fields.BooleanField: null_boolean>',
             '<yepes.contrib.datamigrations.fields.BooleanField: null_boolean_as_string>'],
        )
        self.assertEqual(migration.fields_to_export, migration.fields)
        self.assertEqual(migration.fields_to_import, migration.fields)
        self.assertEqual(
            repr(migration.primary_key),
            '<yepes.contrib.datamigrations.fields.IntegerField: id>',
        )
        self.assertIsNone(migration.natural_foreign_keys)
        self.assertTrue(migration.can_create)
        self.assertTrue(migration.can_export)
        self.assertTrue(migration.can_import)
        self.assertTrue(migration.can_update)
        self.assertFalse(migration.requires_model_instances)

    def test_datetime_model(self):
        migration = ModelMigration(DateTimeModel)
        self.assertEqual(
            [repr(fld) for fld in migration.fields],
            ['<yepes.contrib.datamigrations.fields.IntegerField: id>',
             '<yepes.contrib.datamigrations.fields.DateField: date>',
             '<yepes.contrib.datamigrations.fields.DateTimeField: datetime>',
             '<yepes.contrib.datamigrations.fields.TimeField: time>'],
        )
        self.assertEqual(migration.fields_to_export, migration.fields)
        self.assertEqual(migration.fields_to_import, migration.fields)
        self.assertEqual(
            repr(migration.primary_key),
            '<yepes.contrib.datamigrations.fields.IntegerField: id>',
        )
        self.assertIsNone(migration.natural_foreign_keys)
        self.assertTrue(migration.can_create)
        self.assertTrue(migration.can_export)
        self.assertTrue(migration.can_import)
        self.assertTrue(migration.can_update)
        self.assertFalse(migration.requires_model_instances)

        migration = ModelMigration(
            DateTimeModel,
            use_natural_primary_keys=True,
            use_natural_foreign_keys=True,
        )
        self.assertEqual(
            [repr(fld) for fld in migration.fields],
            ['<yepes.contrib.datamigrations.fields.IntegerField: id>',
             '<yepes.contrib.datamigrations.fields.DateField: date>',
             '<yepes.contrib.datamigrations.fields.DateTimeField: datetime>',
             '<yepes.contrib.datamigrations.fields.TimeField: time>'],
        )
        self.assertEqual(migration.fields_to_export, migration.fields)
        self.assertEqual(migration.fields_to_import, migration.fields)
        self.assertEqual(
            repr(migration.primary_key),
            '<yepes.contrib.datamigrations.fields.IntegerField: id>',
        )
        self.assertIsNone(migration.natural_foreign_keys)
        self.assertTrue(migration.can_create)
        self.assertTrue(migration.can_export)
        self.assertTrue(migration.can_import)
        self.assertTrue(migration.can_update)
        self.assertFalse(migration.requires_model_instances)

    def test_numeric_model(self):
        migration = ModelMigration(NumericModel)
        self.assertEqual(
            [repr(fld) for fld in migration.fields],
            ['<yepes.contrib.datamigrations.fields.IntegerField: id>',
             '<yepes.contrib.datamigrations.fields.IntegerField: integer>',
             '<yepes.contrib.datamigrations.fields.IntegerField: integer_as_string>',
             '<yepes.contrib.datamigrations.fields.FloatField: float>',
             '<yepes.contrib.datamigrations.fields.FloatField: float_as_string>',
             '<yepes.contrib.datamigrations.fields.NumberField: decimal>',
             '<yepes.contrib.datamigrations.fields.NumberField: decimal_as_string>'],
        )
        self.assertEqual(migration.fields_to_export, migration.fields)
        self.assertEqual(migration.fields_to_import, migration.fields)
        self.assertEqual(
            repr(migration.primary_key),
            '<yepes.contrib.datamigrations.fields.IntegerField: id>',
        )
        self.assertIsNone(migration.natural_foreign_keys)
        self.assertTrue(migration.can_create)
        self.assertTrue(migration.can_export)
        self.assertTrue(migration.can_import)
        self.assertTrue(migration.can_update)
        self.assertFalse(migration.requires_model_instances)

        migration = ModelMigration(
            NumericModel,
            use_natural_primary_keys=True,
            use_natural_foreign_keys=True,
        )
        self.assertEqual(
            [repr(fld) for fld in migration.fields],
            ['<yepes.contrib.datamigrations.fields.IntegerField: id>',
             '<yepes.contrib.datamigrations.fields.IntegerField: integer>',
             '<yepes.contrib.datamigrations.fields.IntegerField: integer_as_string>',
             '<yepes.contrib.datamigrations.fields.FloatField: float>',
             '<yepes.contrib.datamigrations.fields.FloatField: float_as_string>',
             '<yepes.contrib.datamigrations.fields.NumberField: decimal>',
             '<yepes.contrib.datamigrations.fields.NumberField: decimal_as_string>'],
        )
        self.assertEqual(migration.fields_to_export, migration.fields)
        self.assertEqual(migration.fields_to_import, migration.fields)
        self.assertEqual(
            repr(migration.primary_key),
            '<yepes.contrib.datamigrations.fields.IntegerField: id>',
        )
        self.assertIsNone(migration.natural_foreign_keys)
        self.assertTrue(migration.can_create)
        self.assertTrue(migration.can_export)
        self.assertTrue(migration.can_import)
        self.assertTrue(migration.can_update)
        self.assertFalse(migration.requires_model_instances)

    def test_text_model(self):
        migration = ModelMigration(TextModel)
        self.assertEqual(
            [repr(fld) for fld in migration.fields],
            ['<yepes.contrib.datamigrations.fields.IntegerField: id>',
             '<yepes.contrib.datamigrations.fields.TextField: char>',
             '<yepes.contrib.datamigrations.fields.TextField: text>'],
        )
        self.assertEqual(migration.fields_to_export, migration.fields)
        self.assertEqual(migration.fields_to_import, migration.fields)
        self.assertEqual(
            repr(migration.primary_key),
            '<yepes.contrib.datamigrations.fields.IntegerField: id>',
        )
        self.assertIsNone(migration.natural_foreign_keys)
        self.assertTrue(migration.can_create)
        self.assertTrue(migration.can_export)
        self.assertTrue(migration.can_import)
        self.assertTrue(migration.can_update)
        self.assertFalse(migration.requires_model_instances)

        migration = ModelMigration(
            TextModel,
            use_natural_primary_keys=True,
            use_natural_foreign_keys=True,
        )
        self.assertEqual(
            [repr(fld) for fld in migration.fields],
            ['<yepes.contrib.datamigrations.fields.IntegerField: id>',
             '<yepes.contrib.datamigrations.fields.TextField: char>',
             '<yepes.contrib.datamigrations.fields.TextField: text>'],
        )
        self.assertEqual(migration.fields_to_export, migration.fields)
        self.assertEqual(migration.fields_to_import, migration.fields)
        self.assertEqual(
            repr(migration.primary_key),
            '<yepes.contrib.datamigrations.fields.IntegerField: id>',
        )
        self.assertIsNone(migration.natural_foreign_keys)
        self.assertTrue(migration.can_create)
        self.assertTrue(migration.can_export)
        self.assertTrue(migration.can_import)
        self.assertTrue(migration.can_update)
        self.assertFalse(migration.requires_model_instances)

    def test_filter_migration_fields(self):
        migration = ModelMigration(BlogCategoryModel, fields=[
            'pk',
            'name',
            'description',
        ], exclude=[
            'pk',
        ])
        self.assertEqual(
            [repr(fld) for fld in migration.fields],
            ['<yepes.contrib.datamigrations.fields.TextField: name>',
             '<yepes.contrib.datamigrations.fields.TextField: description>'],
        )
        self.assertEqual(migration.fields_to_export, migration.fields)
        self.assertEqual(migration.fields_to_import, migration.fields)
        self.assertIsNone(migration.primary_key)
        self.assertIsNone(migration.natural_foreign_keys)
        self.assertFalse(migration.can_create)
        self.assertTrue(migration.can_export)
        self.assertFalse(migration.can_import)
        self.assertFalse(migration.can_update)
        self.assertFalse(migration.requires_model_instances)

        migration = ModelMigration(BlogCategoryModel, fields=[
            'pk',
            'name',
            'blog__name',
        ])
        self.assertEqual(
            [repr(fld) for fld in migration.fields],
            ['<yepes.contrib.datamigrations.fields.IntegerField: id>',
             '<yepes.contrib.datamigrations.fields.TextField: name>',
             '<yepes.contrib.datamigrations.fields.TextField: blog__name (blog_id__name)>'],
        )
        self.assertEqual(migration.fields_to_export, migration.fields)
        self.assertEqual(migration.fields_to_import, migration.fields)
        self.assertEqual(
            repr(migration.primary_key),
            '<yepes.contrib.datamigrations.fields.IntegerField: id>',
        )
        self.assertEqual(
            [repr(fld) for fld in migration.natural_foreign_keys],
            ['<yepes.contrib.datamigrations.fields.TextField: blog__name (blog_id__name)>'],
        )
        self.assertTrue(migration.can_create)
        self.assertTrue(migration.can_export)
        self.assertTrue(migration.can_import)
        self.assertTrue(migration.can_update)
        self.assertFalse(migration.requires_model_instances)

        migration = ModelMigration(BlogCategoryModel, fields=[
            'pk',
            'name',
            'description',
            'blog__name',
            'blog__description',
        ])
        self.assertEqual(
            [repr(fld) for fld in migration.fields],
            ['<yepes.contrib.datamigrations.fields.IntegerField: id>',
             '<yepes.contrib.datamigrations.fields.TextField: name>',
             '<yepes.contrib.datamigrations.fields.TextField: description>',
             '<yepes.contrib.datamigrations.fields.TextField: blog__name (blog_id__name)>',
             '<yepes.contrib.datamigrations.fields.TextField: blog__description (blog_id__description)>'],
        )
        self.assertEqual(migration.fields_to_export, migration.fields)
        self.assertEqual(
            [repr(fld) for fld in migration.fields_to_import],
            ['<yepes.contrib.datamigrations.fields.IntegerField: id>',
             '<yepes.contrib.datamigrations.fields.TextField: name>',
             '<yepes.contrib.datamigrations.fields.TextField: description>',
             '<yepes.contrib.datamigrations.fields.TextField: blog__name (blog_id__name)>'],
        )
        self.assertEqual(
            repr(migration.primary_key),
            '<yepes.contrib.datamigrations.fields.IntegerField: id>',
        )
        self.assertEqual(
            [repr(fld) for fld in migration.natural_foreign_keys],
            ['<yepes.contrib.datamigrations.fields.TextField: blog__name (blog_id__name)>'],
        )
        self.assertTrue(migration.can_create)
        self.assertTrue(migration.can_export)
        self.assertTrue(migration.can_import)
        self.assertTrue(migration.can_update)
        self.assertFalse(migration.requires_model_instances)

    def test_natural_keys(self):
        migration = ModelMigration(
            BlogCategoryModel,
            use_natural_primary_keys=True,
            use_natural_foreign_keys=False,
        )
        self.assertEqual(
            [repr(fld) for fld in migration.fields],
            ['<yepes.contrib.datamigrations.fields.IntegerField: blog (blog_id)>',
             '<yepes.contrib.datamigrations.fields.TextField: name>',
             '<yepes.contrib.datamigrations.fields.TextField: description>'],
        )
        self.assertEqual(migration.fields_to_export, migration.fields)
        self.assertEqual(migration.fields_to_import, migration.fields)
        self.assertEqual(
            [repr(fld) for fld in migration.primary_key],
            ['<yepes.contrib.datamigrations.fields.IntegerField: blog (blog_id)>',
             '<yepes.contrib.datamigrations.fields.TextField: name>'],
        )
        self.assertIsNone(migration.natural_foreign_keys)
        self.assertTrue(migration.can_create)
        self.assertTrue(migration.can_export)
        self.assertTrue(migration.can_import)
        self.assertTrue(migration.can_update)
        self.assertFalse(migration.requires_model_instances)

        migration = ModelMigration(
            BlogCategoryModel,
            use_natural_primary_keys=False,
            use_natural_foreign_keys=True,
        )
        self.assertEqual(
            [repr(fld) for fld in migration.fields],
            ['<yepes.contrib.datamigrations.fields.IntegerField: id>',
             '<yepes.contrib.datamigrations.fields.TextField: blog__name>',
             '<yepes.contrib.datamigrations.fields.TextField: name>',
             '<yepes.contrib.datamigrations.fields.TextField: description>'],
        )
        self.assertEqual(migration.fields_to_export, migration.fields)
        self.assertEqual(migration.fields_to_import, migration.fields)
        self.assertEqual(
            repr(migration.primary_key),
            '<yepes.contrib.datamigrations.fields.IntegerField: id>',
        )
        self.assertEqual(
            [repr(fld) for fld in migration.natural_foreign_keys],
            ['<yepes.contrib.datamigrations.fields.TextField: blog__name>'],
        )
        self.assertTrue(migration.can_create)
        self.assertTrue(migration.can_export)
        self.assertTrue(migration.can_import)
        self.assertTrue(migration.can_update)
        self.assertFalse(migration.requires_model_instances)

        migration = ModelMigration(
            BlogCategoryModel,
            use_natural_primary_keys=True,
            use_natural_foreign_keys=True,
        )
        self.assertEqual(
            [repr(fld) for fld in migration.fields],
            ['<yepes.contrib.datamigrations.fields.TextField: blog__name>',
             '<yepes.contrib.datamigrations.fields.TextField: name>',
             '<yepes.contrib.datamigrations.fields.TextField: description>'],
        )
        self.assertEqual(migration.fields_to_export, migration.fields)
        self.assertEqual(migration.fields_to_import, migration.fields)
        self.assertEqual(
            [repr(fld) for fld in migration.primary_key],
            ['<yepes.contrib.datamigrations.fields.TextField: blog__name>',
             '<yepes.contrib.datamigrations.fields.TextField: name>'],
        )
        self.assertEqual(
            [repr(fld) for fld in migration.natural_foreign_keys],
            ['<yepes.contrib.datamigrations.fields.TextField: blog__name>'],
        )
        self.assertTrue(migration.can_create)
        self.assertTrue(migration.can_export)
        self.assertTrue(migration.can_import)
        self.assertTrue(migration.can_update)
        self.assertFalse(migration.requires_model_instances)


class QuerySetExportationsTests(TempDirMixin, test.TestCase):

    maxDiff = None
    tempDirPrefix = 'test_data_migrations_'

    def setUp(self):
        super(QuerySetExportationsTests, self).setUp()
        migration = BlogMigration(BlogModel)
        source_path = os.path.join(MIGRATIONS_DIR, 'blog_result.json')
        with open(source_path, 'rt') as source_file:
            migration.import_data(source_file, plan='create')

        migration = BlogCategoryMigration(BlogCategoryModel)
        source_path = os.path.join(MIGRATIONS_DIR, 'blog_category_result.json')
        with open(source_path, 'rt') as source_file:
            migration.import_data(source_file, plan='direct')

    def test_all_fields(self):
        migration = QuerySetExportation(BlogCategoryModel.objects.all())
        self.assertEqual(
            [repr(fld) for fld in migration.fields],
            ['<yepes.contrib.datamigrations.fields.IntegerField: id>',
             '<yepes.contrib.datamigrations.fields.IntegerField: blog (blog_id)>',
             '<yepes.contrib.datamigrations.fields.TextField: name>',
             '<yepes.contrib.datamigrations.fields.TextField: description>'],
        )
        self.assertEqual(migration.fields_to_export, migration.fields)
        self.assertEqual(migration.fields_to_import, [])
        self.assertIsNone(migration.primary_key)
        self.assertIsNone(migration.natural_foreign_keys)
        self.assertFalse(migration.can_create)
        self.assertTrue(migration.can_export)
        self.assertFalse(migration.can_import)
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
        with self.assertRaises(UnableToImportError):
            migration.import_data('')

    def test_selected_fields(self):
        migration = QuerySetExportation(BlogCategoryModel.objects.only('id', 'name'))
        self.assertEqual(
            [repr(fld) for fld in migration.fields],
            ['<yepes.contrib.datamigrations.fields.IntegerField: id>',
             '<yepes.contrib.datamigrations.fields.TextField: name>'],
        )
        self.assertEqual(migration.fields_to_export, migration.fields)
        self.assertEqual(migration.fields_to_import, [])
        self.assertIsNone(migration.primary_key)
        self.assertIsNone(migration.natural_foreign_keys)
        self.assertFalse(migration.can_create)
        self.assertTrue(migration.can_export)
        self.assertFalse(migration.can_import)
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
        with self.assertRaises(UnableToImportError):
            migration.import_data('')

    def test_excluded_fields(self):
        migration = QuerySetExportation(BlogCategoryModel.objects.defer('description'))
        self.assertEqual(
            [repr(fld) for fld in migration.fields],
            ['<yepes.contrib.datamigrations.fields.IntegerField: id>',
             '<yepes.contrib.datamigrations.fields.IntegerField: blog (blog_id)>',
             '<yepes.contrib.datamigrations.fields.TextField: name>'],
        )
        self.assertEqual(migration.fields_to_export, migration.fields)
        self.assertEqual(migration.fields_to_import, [])
        self.assertIsNone(migration.primary_key)
        self.assertIsNone(migration.natural_foreign_keys)
        self.assertFalse(migration.can_create)
        self.assertTrue(migration.can_export)
        self.assertFalse(migration.can_import)
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
        with self.assertRaises(UnableToImportError):
            migration.import_data('')

    def test_evaluated_queryset(self):
        qs = BlogCategoryModel.objects.all()
        len(qs)  # Evaluate queryset
        migration = QuerySetExportation(qs)
        self.assertEqual(
            [repr(fld) for fld in migration.fields],
            ['<yepes.contrib.datamigrations.fields.IntegerField: id>',
             '<yepes.contrib.datamigrations.fields.IntegerField: blog (blog_id)>',
             '<yepes.contrib.datamigrations.fields.TextField: name>',
             '<yepes.contrib.datamigrations.fields.TextField: description>'],
        )
        self.assertEqual(migration.fields_to_export, migration.fields)
        self.assertEqual(migration.fields_to_import, [])
        self.assertIsNone(migration.primary_key)
        self.assertIsNone(migration.natural_foreign_keys)
        self.assertFalse(migration.can_create)
        self.assertTrue(migration.can_export)
        self.assertFalse(migration.can_import)
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
        with self.assertRaises(UnableToImportError):
            migration.import_data('')

    def test_filtered_queryset(self):
        qs = BlogCategoryModel.objects.all()
        migration = QuerySetExportation(qs.filter(name__startswith='S'))
        self.assertEqual(
            [repr(fld) for fld in migration.fields],
            ['<yepes.contrib.datamigrations.fields.IntegerField: id>',
             '<yepes.contrib.datamigrations.fields.IntegerField: blog (blog_id)>',
             '<yepes.contrib.datamigrations.fields.TextField: name>',
             '<yepes.contrib.datamigrations.fields.TextField: description>'],
        )
        self.assertEqual(migration.fields_to_export, migration.fields)
        self.assertEqual(migration.fields_to_import, [])
        self.assertIsNone(migration.primary_key)
        self.assertIsNone(migration.natural_foreign_keys)
        self.assertFalse(migration.can_create)
        self.assertTrue(migration.can_export)
        self.assertFalse(migration.can_import)
        self.assertFalse(migration.can_update)
        self.assertFalse(migration.requires_model_instances)
        self.assertJSONEqual(
            migration.export_data(),
            """[
                {"id": 6, "blog": 5, "name": "State Secrets", "description": "Political scandals and things like those."},
                {"id": 7, "blog": 5, "name": "Some Nonsense", "description": "This cannot be described."}
            ]""")
        with self.assertRaises(UnableToImportError):
            migration.import_data('')

    def test_sliced_queryset(self):
        qs = BlogCategoryModel.objects.all()
        migration = QuerySetExportation(qs[0:4])
        self.assertEqual(
            [repr(fld) for fld in migration.fields],
            ['<yepes.contrib.datamigrations.fields.IntegerField: id>',
             '<yepes.contrib.datamigrations.fields.IntegerField: blog (blog_id)>',
             '<yepes.contrib.datamigrations.fields.TextField: name>',
             '<yepes.contrib.datamigrations.fields.TextField: description>'],
        )
        self.assertEqual(migration.fields_to_export, migration.fields)
        self.assertEqual(migration.fields_to_import, [])
        self.assertIsNone(migration.primary_key)
        self.assertIsNone(migration.natural_foreign_keys)
        self.assertFalse(migration.can_create)
        self.assertTrue(migration.can_export)
        self.assertFalse(migration.can_import)
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
        with self.assertRaises(UnableToImportError):
            migration.import_data('')

    def test_sorted_queryset(self):
        qs = BlogCategoryModel.objects.all()
        migration = QuerySetExportation(qs.order_by('name'))
        self.assertEqual(
            [repr(fld) for fld in migration.fields],
            ['<yepes.contrib.datamigrations.fields.IntegerField: id>',
             '<yepes.contrib.datamigrations.fields.IntegerField: blog (blog_id)>',
             '<yepes.contrib.datamigrations.fields.TextField: name>',
             '<yepes.contrib.datamigrations.fields.TextField: description>'],
        )
        self.assertEqual(migration.fields_to_export, migration.fields)
        self.assertEqual(migration.fields_to_import, [])
        self.assertIsNone(migration.primary_key)
        self.assertIsNone(migration.natural_foreign_keys)
        self.assertFalse(migration.can_create)
        self.assertTrue(migration.can_export)
        self.assertFalse(migration.can_import)
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
        with self.assertRaises(UnableToImportError):
            migration.import_data('')

