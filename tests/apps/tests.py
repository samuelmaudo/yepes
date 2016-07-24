# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from django import test
from django.core.exceptions import ImproperlyConfigured

from yepes.apps import apps
from yepes.apps.registry import Apps


class GetClassTest(test.SimpleTestCase):

    def test_valid_class(self):
        cls = apps.get_class('registry.base', 'Registry')
        from yepes.contrib.registry.base import Registry
        self.assertEqual(cls, Registry)
        self.assertIs(cls, Registry)

    def test_missing_app(self):
        with self.assertRaises(LookupError):
            apps.get_class('asdfg.base', 'Registry')

    def test_missing_module(self):
        with self.assertRaises(LookupError):
            apps.get_class('registry.asdfg', 'Registry')

    def test_missing_class(self):
        with self.assertRaises(LookupError):
            apps.get_class('registry.base', 'asdfg')

    def test_shortcut(self):
        cls = apps.get_class('registry.base.Registry')
        from yepes.contrib.registry.base import Registry
        self.assertEqual(cls, Registry)
        self.assertIs(cls, Registry)


class GetModelTest(test.SimpleTestCase):

    def test_valid_model(self):
        model = apps.get_model('registry', 'Entry')
        from yepes.contrib.registry.models import Entry
        self.assertEqual(model, Entry)
        self.assertIs(model, Entry)

    def test_missing_app(self):
        with self.assertRaises(LookupError):
            apps.get_model('asdfg.template', 'Entry')

    def test_missing_model(self):
        with self.assertRaises(LookupError):
            apps.get_model('registry', 'asdfg')

    def test_shortcut(self):
        model = apps.get_model('registry.Entry')
        from yepes.contrib.registry.models import Entry
        self.assertEqual(model, Entry)
        self.assertIs(model, Entry)


class GetModelsTest(test.SimpleTestCase):

    def test_default_models(self):
        models = list(apps.get_models())
        from django.contrib.auth.models import Group, User
        from django.contrib.contenttypes.models import ContentType
        from django.contrib.sites.models import Site
        from yepes.contrib.registry.models import Entry, LongEntry
        self.assertIn(Group, models)
        self.assertIn(User, models)
        self.assertIn(ContentType, models)
        self.assertIn(Site, models)
        self.assertIn(Entry, models)
        self.assertIn(LongEntry, models)


@test.override_settings(INSTALLED_APPS=[
    'apps.overriding.apps.AppConfig',
    'apps.overridable.apps.AppConfig',
])
class OverridingConfigTest(test.SimpleTestCase):

    def test_config_attributes(self):
        overriding, overridable = apps.get_app_configs()
        self.assertEqual(overriding.label, 'overriding')
        self.assertEqual(overriding.name, 'apps.overriding')
        self.assertEqual(overriding.overridden_app_label, 'overridable')
        self.assertEqual(overriding.overridden_app_config, overridable)
        self.assertEqual(overridable.label, 'overridable')
        self.assertEqual(overridable.name, 'apps.overridable')
        self.assertEqual(overridable.overriding_app_configs, [overriding])

    def test_get_class(self):
        overriding, overridable = apps.get_app_configs()
        Article = apps.get_class('overridable.models', 'Article')
        self.assertEqual(Article.__module__, 'apps.overriding.models')
        self.assertEqual(Article.__name__, 'Article')
        self.assertEqual(Article, overridable.get_class('models', 'Article'))
        self.assertEqual(Article, overriding.get_class('models', 'Article'))

        Author = apps.get_class('overridable.models', 'Author')
        self.assertEqual(Author.__module__, 'apps.overridable.models')
        self.assertEqual(Author.__name__, 'Author')
        self.assertEqual(Author, overridable.get_class('models', 'Author'))
        with self.assertRaises(LookupError):
            overriding.get_class('models', 'Author')

    def test_get_model(self):
        overriding, overridable = apps.get_app_configs()
        Article = apps.get_model('overridable', 'Article')
        self.assertEqual(Article, overridable.get_model('Article'))
        with self.assertRaises(LookupError):
            overriding.get_model('Article')

        article_field_names = {
            field.name
            for field
            in Article._meta.get_fields()
        }
        self.assertIn('extract', article_field_names)
        self.assertEqual(article_field_names, {
            'id',
            'title',
            'extract',
            'content',
            'author',
        })
        Author = apps.get_model('overridable', 'Author')
        self.assertEqual(Author, overridable.get_model('Author'))
        with self.assertRaises(LookupError):
            overriding.get_model('Author')

        author_field_names = {
            field.name
            for field
            in Author._meta.get_fields()
        }
        self.assertEqual(author_field_names, {'id', 'name', 'articles'})

    def test_invalid_target(self):
        app_list = [
            'apps.invalid_target.apps.AppConfig',
            'apps.non_overridable',
        ]
        with self.assertRaises(ImproperlyConfigured):
            with self.settings(INSTALLED_APPS=app_list):
                pass

    def test_missing_target(self):
        app_list = [
            'apps.missing_target.apps.AppConfig',
        ]
        with self.assertRaises(LookupError):
            with self.settings(INSTALLED_APPS=app_list):
                pass

    def test_no_target(self):
        app_list = [
            'apps.no_target.apps.AppConfig',
        ]
        with self.assertRaises(ImproperlyConfigured):
            with self.settings(INSTALLED_APPS=app_list):
                pass

