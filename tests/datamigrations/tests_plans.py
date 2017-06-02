# -*- coding:utf-8 -*-

from __future__ import unicode_literals

import collections
from io import open
from itertools import chain
import os

from django import test
from django.utils.encoding import force_str
from django.utils._os import upath

from yepes.contrib.datamigrations.importation_plans import (
    importation_plans,
    PlanRegistry,
)
from yepes.contrib.datamigrations.importation_plans.bulk_create import BulkCreatePlan
from yepes.contrib.datamigrations.importation_plans.create import CreatePlan
from yepes.contrib.datamigrations.importation_plans.direct import DirectPlan
from yepes.contrib.datamigrations.importation_plans.replace import ReplacePlan
from yepes.contrib.datamigrations.importation_plans.replace_all import ReplaceAllPlan
from yepes.contrib.datamigrations.importation_plans.update import UpdatePlan
from yepes.contrib.datamigrations.importation_plans.update_or_bulk_create import UpdateOrBulkCreatePlan
from yepes.contrib.datamigrations.importation_plans.update_or_create import UpdateOrCreatePlan
from yepes.test_mixins import TempDirMixin

from .data_migrations import (
    AlphabetMigration,
    AuthorMigration,
    BlogMigration,
    BlogCategoryMigration,
)
from .models import (
    AlphabetModel,
    AuthorModel,
    BlogModel,
    BlogCategoryModel,
    PostModel,
)

MODULE_DIR = os.path.abspath(os.path.dirname(upath(__file__)))
MIGRATIONS_DIR = os.path.join(MODULE_DIR, 'data_migrations')


class PlanRegistryTests(test.TestCase):

    maxDiff = None

    def setUp(self):
        super(PlanRegistryTests, self).setUp()
        self.assertEqual('bulk_create', BulkCreatePlan.name)
        self.assertEqual('create', CreatePlan.name)
        self.assertEqual('direct', DirectPlan.name)
        self.assertEqual('replace', ReplacePlan.name)
        self.assertEqual('replace_all', ReplaceAllPlan.name)
        self.assertEqual('update', UpdatePlan.name)
        self.assertEqual('update_or_bulk_create', UpdateOrBulkCreatePlan.name)
        self.assertEqual('update_or_create', UpdateOrCreatePlan.name)

    def test_registry_class(self):
        registry = PlanRegistry()
        self.assertEqual(
                set(),
                set(registry.get_plans()))

        self.assertTrue(
                registry.register_plan(CreatePlan))
        self.assertEqual(
                {CreatePlan},
                set(registry.get_plans()))

        self.assertTrue(
                registry.register_plan('yepes.contrib.datamigrations.importation_plans.update.UpdatePlan'))
        self.assertEqual(
                {CreatePlan, UpdatePlan},
                set(registry.get_plans()))

        self.assertFalse(
                registry.register_plan('yepes.contrib.datamigrations.importation_plans.update.MissingPlan'))
        self.assertEqual(
                {CreatePlan, UpdatePlan},
                set(registry.get_plans()))

        self.assertTrue('create' in registry)
        self.assertTrue('update' in registry)
        self.assertFalse('replace' in registry)
        self.assertTrue(registry.has_plan('create'))
        self.assertTrue(registry.has_plan('update'))
        self.assertFalse(registry.has_plan('replace'))
        self.assertIs(registry.get_plan('create'), CreatePlan)
        self.assertIs(registry.get_plan('update'), UpdatePlan)
        with self.assertRaisesRegexp(LookupError, "Importation plan 'replace' could not be found."):
            registry.get_plan('replace')

    def test_default_registry_object(self):
        self.assertEqual(
            {
                BulkCreatePlan, CreatePlan, DirectPlan,
                ReplacePlan, ReplaceAllPlan, UpdatePlan,
                UpdateOrBulkCreatePlan, UpdateOrCreatePlan,
            },
            set(importation_plans.get_plans()),
        )
        self.assertTrue('bulk_create' in importation_plans)
        self.assertTrue('create' in importation_plans)
        self.assertTrue('direct' in importation_plans)
        self.assertTrue('replace' in importation_plans)
        self.assertTrue('replace_all' in importation_plans)
        self.assertTrue('update' in importation_plans)
        self.assertTrue('update_or_bulk_create' in importation_plans)
        self.assertTrue('update_or_create' in importation_plans)


class ImportationPlansTests(test.TestCase):

    source_1 = force_str("""pk,letter,word
1,a,alfa
2,b,bravo
3,c,charlie
4,d,delta
5,e,echo
""")
    source_2 = force_str("""pk,letter,word
6,f,foxtrot
7,g,golf
8,h,hotel
9,i,india
10,j,juliett
""")
    source_3 = force_str("""pk,letter,word
11,k,kilo
12,l,lima
13,m,mike
14,n,november
15,o,oscar
""")
    source_4 = force_str("""pk,letter,word
1,a,alfa
2,b,bravo
3,c,charlie
4,d,delta
5,e,echo
6,f,frank
7,g,george
8,h,henry
9,i,ida
10,j,john
11,k,kilo
12,l,lima
13,m,mike
14,n,november
15,o,oscar
""")
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
            ['<yepes.contrib.datamigrations.fields.IntegerField: pk>',
             '<yepes.contrib.datamigrations.fields.TextField: letter>',
             '<yepes.contrib.datamigrations.fields.TextField: word>'],
        )
        self.assertEqual(
            [repr(fld) for fld in migration.fields_to_import],
            ['<yepes.contrib.datamigrations.fields.IntegerField: pk>',
             '<yepes.contrib.datamigrations.fields.TextField: letter>',
             '<yepes.contrib.datamigrations.fields.TextField: word>'],
        )
        self.assertEqual(
            repr(migration.primary_key),
            '<yepes.contrib.datamigrations.fields.IntegerField: pk>',
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

    def test_replace_plan(self):
        migration = AlphabetMigration(AlphabetModel)
        serializer = 'csv'
        plan = 'replace'
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

    def test_replace_all_plan(self):
        migration = AlphabetMigration(AlphabetModel)
        serializer = 'csv'
        plan = 'replace_all'
        migration.import_data(self.source_1, serializer, plan)
        objs = AlphabetModel.objects.all()
        self.assertEqual(len(objs), 5)
        for i, word in enumerate(self.words_1):
            obj = objs[i]
            self.assertEqual(obj.pk, i + 1)
            self.assertEqual(obj.letter, word[0])
            self.assertEqual(obj.word, word)

        migration.import_data(self.source_3, serializer, plan)
        objs = AlphabetModel.objects.all()
        self.assertEqual(len(objs), 5)
        for i, word in enumerate(self.words_3):
            obj = objs[i]
            self.assertEqual(obj.pk, i + 11)
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
    tempDirPrefix = 'test_data_migrations_'

    def test_data_migrations(self):
        migration = AuthorMigration(AuthorModel)
        self.assertEqual(
            [repr(fld) for fld in migration.fields],
            ['<yepes.contrib.datamigrations.fields.TextField: name>',
             '<yepes.contrib.datamigrations.fields.FileField: image>'],
        )
        self.assertEqual(
            [repr(fld) for fld in migration.fields_to_import],
            ['<yepes.contrib.datamigrations.fields.TextField: name>',
             '<yepes.contrib.datamigrations.fields.FileField: image>'],
        )
        self.assertEqual(
            repr(migration.primary_key),
            '<yepes.contrib.datamigrations.fields.TextField: name>',
        )
        self.assertIsNone(migration.natural_foreign_keys)
        self.assertTrue(migration.can_create)
        self.assertTrue(migration.can_update)
        self.assertFalse(migration.requires_model_instances)

        migration = BlogMigration(BlogModel)
        self.assertEqual(
            [repr(fld) for fld in migration.fields],
            ['<yepes.contrib.datamigrations.fields.TextField: name>',
             '<yepes.contrib.datamigrations.fields.TextField: description>'],
        )
        self.assertEqual(
            [repr(fld) for fld in migration.fields_to_import],
            ['<yepes.contrib.datamigrations.fields.TextField: name>',
             '<yepes.contrib.datamigrations.fields.TextField: description>'],
        )
        self.assertEqual(
            repr(migration.primary_key),
            '<yepes.contrib.datamigrations.fields.TextField: name>',
        )
        self.assertIsNone(migration.natural_foreign_keys)
        self.assertTrue(migration.can_create)
        self.assertTrue(migration.can_update)
        self.assertFalse(migration.requires_model_instances)

        migration = BlogCategoryMigration(BlogCategoryModel)
        self.assertEqual(
            [repr(fld) for fld in migration.fields],
            ['<yepes.contrib.datamigrations.fields.TextField: blog__name>',
             '<yepes.contrib.datamigrations.fields.TextField: name>',
             '<yepes.contrib.datamigrations.fields.TextField: description>'],
        )
        self.assertEqual(
            [repr(fld) for fld in migration.fields_to_import],
            ['<yepes.contrib.datamigrations.fields.TextField: blog__name>',
             '<yepes.contrib.datamigrations.fields.TextField: name>',
             '<yepes.contrib.datamigrations.fields.TextField: description>'],
        )
        self.assertEqual(
            [repr(k) for k in migration.primary_key],
            ['<yepes.contrib.datamigrations.fields.TextField: blog__name>',
             '<yepes.contrib.datamigrations.fields.TextField: name>'],
        )
        self.assertEqual(
            [repr(k) for k in migration.natural_foreign_keys],
            ['<yepes.contrib.datamigrations.fields.TextField: blog__name>'],
        )
        self.assertTrue(migration.can_create)
        self.assertTrue(migration.can_update)
        self.assertFalse(migration.requires_model_instances)

    def test_create_and_update_plans(self):
        migration = AuthorMigration(AuthorModel)
        self.assertEqual(migration.primary_key.path, 'name')

        source_path = os.path.join(MIGRATIONS_DIR, 'author_source.json')
        with open(source_path, 'rt') as source_file:

            migration.import_data(source_file.read(), plan='create')
            result = migration.export_data()
            source_file.seek(0)
            self.assertEqual(
                    result.splitlines(),
                    source_file.read().splitlines())

        migration = BlogMigration(BlogModel)
        self.assertEqual(migration.primary_key.path, 'name')

        source_path = os.path.join(MIGRATIONS_DIR, 'blog_source.json')
        update_path = os.path.join(MIGRATIONS_DIR, 'blog_update.json')
        expected_path = os.path.join(MIGRATIONS_DIR, 'blog_result.json')
        with open(source_path, 'rt') as source_file:
            with open(update_path, 'rt') as update_file:
                with open(expected_path, 'rt') as expected_file:

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
        source_path = os.path.join(MIGRATIONS_DIR, 'blog_category_source.json')
        update_path = os.path.join(MIGRATIONS_DIR, 'blog_category_update.json')
        expected_path = os.path.join(MIGRATIONS_DIR, 'blog_category_result.json')
        with open(source_path, 'rt') as source_file:
            with open(update_path, 'rt') as update_file:
                with open(expected_path, 'rt') as expected_file:

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

        source_path = os.path.join(MIGRATIONS_DIR, 'author_source.json')
        with open(source_path, 'rt') as source_file:

            migration.import_data(source_file.read(), plan='bulk_create')
            result = migration.export_data()
            source_file.seek(0)
            self.assertEqual(
                    result.splitlines(),
                    source_file.read().splitlines())

        migration = BlogMigration(BlogModel)
        self.assertEqual(migration.primary_key.path, 'name')

        source_path = os.path.join(MIGRATIONS_DIR, 'blog_source.json')
        update_path = os.path.join(MIGRATIONS_DIR, 'blog_update.json')
        expected_path = os.path.join(MIGRATIONS_DIR, 'blog_result.json')
        with open(source_path, 'rt') as source_file:
            with open(update_path, 'rt') as update_file:
                with open(expected_path, 'rt') as expected_file:

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
        source_path = os.path.join(MIGRATIONS_DIR, 'blog_category_source.json')
        update_path = os.path.join(MIGRATIONS_DIR, 'blog_category_update.json')
        expected_path = os.path.join(MIGRATIONS_DIR, 'blog_category_result.json')
        with open(source_path, 'rt') as source_file:
            with open(update_path, 'rt') as update_file:
                with open(expected_path, 'rt') as expected_file:

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

        source_path = os.path.join(MIGRATIONS_DIR, 'author_source.json')
        with open(source_path, 'rt') as source_file:

            migration.import_data(source_file.read())
            result = migration.export_data()
            source_file.seek(0)
            self.assertEqual(
                    result.splitlines(),
                    source_file.read().splitlines())

        migration = BlogMigration(BlogModel)
        self.assertEqual(migration.primary_key.path, 'name')

        source_path = os.path.join(MIGRATIONS_DIR, 'blog_source.json')
        update_path = os.path.join(MIGRATIONS_DIR, 'blog_update.json')
        expected_path = os.path.join(MIGRATIONS_DIR, 'blog_result.json')
        with open(source_path, 'rt') as source_file:
            with open(update_path, 'rt') as update_file:
                with open(expected_path, 'rt') as expected_file:

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
        source_path = os.path.join(MIGRATIONS_DIR, 'blog_category_source.json')
        update_path = os.path.join(MIGRATIONS_DIR, 'blog_category_update.json')
        expected_path = os.path.join(MIGRATIONS_DIR, 'blog_category_result.json')
        with open(source_path, 'rt') as source_file:
            with open(update_path, 'rt') as update_file:
                with open(expected_path, 'rt') as expected_file:

                    migration.import_data(source_file.read())
                    migration.import_data(update_file.read())
                    result = migration.export_data()
                    self.assertEqual(
                            result.splitlines(),
                            expected_file.read().splitlines())

    def test_update_or_bulk_create_plan(self):
        migration = AuthorMigration(AuthorModel)
        self.assertEqual(migration.primary_key.path, 'name')

        source_path = os.path.join(MIGRATIONS_DIR, 'author_source.json')
        with open(source_path, 'rt') as source_file:

            migration.import_data(source_file.read(), plan='update_or_bulk_create')
            result = migration.export_data()
            source_file.seek(0)
            self.assertEqual(
                    result.splitlines(),
                    source_file.read().splitlines())

        migration = BlogMigration(BlogModel)
        self.assertEqual(migration.primary_key.path, 'name')

        source_path = os.path.join(MIGRATIONS_DIR, 'blog_source.json')
        update_path = os.path.join(MIGRATIONS_DIR, 'blog_update.json')
        expected_path = os.path.join(MIGRATIONS_DIR, 'blog_result.json')
        with open(source_path, 'rt') as source_file:
            with open(update_path, 'rt') as update_file:
                with open(expected_path, 'rt') as expected_file:

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
        source_path = os.path.join(MIGRATIONS_DIR, 'blog_category_source.json')
        update_path = os.path.join(MIGRATIONS_DIR, 'blog_category_update.json')
        expected_path = os.path.join(MIGRATIONS_DIR, 'blog_category_result.json')
        with open(source_path, 'rt') as source_file:
            with open(update_path, 'rt') as update_file:
                with open(expected_path, 'rt') as expected_file:

                    migration.import_data(source_file.read(), plan='update_or_bulk_create')
                    migration.import_data(update_file.read(), plan='update_or_bulk_create')
                    result = migration.export_data()
                    self.assertEqual(
                            result.splitlines(),
                            expected_file.read().splitlines())

