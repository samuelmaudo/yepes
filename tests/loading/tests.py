# -*- coding:utf-8 -*-

import unittest
import warnings

from django import test

from yepes.loading import (
    LoadingError, MissingAppError, MissingClassError,
    MissingModelError, MissingModuleError, UnavailableAppError,
    get_class, get_classes,
    get_model, get_models,
    get_module,
    LazyClass, LazyModel, LazyModelManager, LazyModelObject,
)

class GetClassTest(test.SimpleTestCase):

    def test_valid_class(self):
        cls = get_class('registry.base', 'Registry')
        from yepes.apps.registry.base import Registry
        self.assertEqual(cls, Registry)
        self.assertIs(cls, Registry)

    def test_missing_app(self):
        with self.assertRaises(MissingAppError):
            get_class('asdfg.base', 'Registry')

    def test_missing_module(self):
        with self.assertRaises(MissingModuleError):
            get_class('registry.asdfg', 'Registry')

    def test_missing_class(self):
        with self.assertRaises(MissingClassError):
            get_class('registry.base', 'asdfg')


class GetClassesTest(test.SimpleTestCase):

    def test_valid_class(self):
        classes = get_classes('registry.base', ['Registry', 'UnregisteredError'])
        from yepes.apps.registry.base import Registry, UnregisteredError
        self.assertEqual(classes, [Registry, UnregisteredError])
        for a, b in zip(classes, [Registry, UnregisteredError]):
            self.assertIs(a, b)

    def test_missing_app(self):
        with self.assertRaises(MissingAppError):
            get_classes('asdfg.base', ['Registry', 'UnregisteredError'])

    def test_missing_module(self):
        with self.assertRaises(MissingModuleError):
            get_classes('registry.asdfg', ['Registry', 'UnregisteredError'])

    def test_missing_class(self):
        with self.assertRaises(MissingClassError):
            get_classes('registry.base', ['Registry', 'asdfg'])


class GetModelTest(test.SimpleTestCase):

    def test_valid_model(self):
        model = get_model('registry', 'Entry')
        from yepes.apps.registry.models import Entry
        self.assertEqual(model, Entry)
        self.assertIs(model, Entry)

    def test_missing_app(self):
        with self.assertRaises(MissingAppError):
            get_model('asdfg.template', 'Entry')

    def test_missing_model(self):
        with self.assertRaises(MissingModelError):
            get_model('registry', 'asdfg')


class GetModelsTest(test.SimpleTestCase):

    def test_valid_model(self):
        models = get_models('registry', ['Entry', 'LongEntry'])
        from yepes.apps.registry.models import Entry, LongEntry
        self.assertEqual(models, [Entry, LongEntry])
        for a, b in zip(models, [Entry, LongEntry]):
            self.assertIs(a, b)

    def test_missing_app(self):
        with self.assertRaises(MissingAppError):
            get_models('asdfg.template', ['Entry', 'LongEntry'])

    def test_missing_model(self):
        with self.assertRaises(MissingModelError):
            get_models('registry', ['Entry', 'asdfg'])

    def test_app_models(self):
        models = get_models('registry')
        from yepes.apps.registry.models import Entry, LongEntry
        self.assertEqual(models, [Entry, LongEntry])
        for a, b in zip(models, [Entry, LongEntry]):
            self.assertIs(a, b)

    def test_app_without_models(self):
        models = get_models('yepes')
        self.assertEqual(models, [])

    def test_all_models(self):
        models = get_models()
        from django.contrib.auth.models import Group, User
        from django.contrib.contenttypes.models import ContentType
        from django.contrib.sites.models import Site
        from yepes.apps.registry.models import Entry, LongEntry
        self.assertIn(Group, models)
        self.assertIn(User, models)
        self.assertIn(ContentType, models)
        self.assertIn(Site, models)
        self.assertIn(Entry, models)
        self.assertIn(LongEntry, models)


class GetModuleTest(test.SimpleTestCase):

    def test_valid_module(self):
        module = get_module('cgi')
        import cgi
        self.assertEqual(module, cgi)
        self.assertIs(module, cgi)

    def test_missing_module(self):
        with self.assertRaises(MissingModuleError):
            get_module('asdfg')

        module = get_module(
            'asdfg',
            ignore_missing=True,
        )
        self.assertIsNone(module)

    def test_invalid_dependency(self):
        with self.assertRaises(ImportError):
            get_module('tests.loading.invalid_dependency')

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter('always')
            module = get_module(
                'tests.loading.invalid_dependency',
                ignore_internal_errors=True,
            )
            self.assertEqual(len(w), 1)
            self.assertTrue(issubclass(w[0].category, ImportWarning))
            self.assertIn('No module', str(w[0].message))
            self.assertIsNone(module)

    def test_invalid_syntax(self):
        with self.assertRaises(SyntaxError):
            get_module('tests.loading.invalid_syntax')

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter('always')
            module = get_module(
                'tests.loading.invalid_syntax',
                ignore_internal_errors=True,
            )
            self.assertEqual(len(w), 1)
            self.assertTrue(issubclass(w[0].category, SyntaxWarning))
            self.assertIn('invalid syntax', str(w[0].message))
            self.assertIsNone(module)


class LazyClassTest(test.SimpleTestCase):

    def test_lazy_loading(self):
        cls = LazyClass('registry.base', 'asdfg')
        with self.assertRaises(MissingClassError):
            cls._meta
        with self.assertRaises(MissingClassError):
            cls._meta = None
        with self.assertRaises(MissingClassError):
            del cls._meta

    def test_class(self):
        cls = LazyClass('registry.base', 'Registry')
        from yepes.apps.registry.base import Registry
        self.assertEqual(cls.__class__, object.__class__)
        self.assertEqual(cls.__class__, Registry.__class__)

    def test_call(self):
        cls = LazyClass('registry.base', 'Registry')
        from yepes.apps.registry.base import Registry
        self.assertIsInstance(cls(), object)
        self.assertIsInstance(cls(), Registry)
        self.assertIsInstance(cls(), cls)

    def test_instance_check(self):
        cls = LazyClass('registry.base', 'Registry')
        from yepes.apps.registry.base import Registry
        self.assertIsInstance(Registry(), cls)
        self.assertIsInstance(cls(), cls)

    @unittest.expectedFailure
    def test_subclass_check(self):
        cls = LazyClass('registry.base', 'Registry')
        from yepes.apps.registry.base import Registry
        self.assertFalse(issubclass(object, Registry))
        self.assertFalse(issubclass(object, cls))
        self.assertTrue(issubclass(Registry, Registry))
        self.assertTrue(issubclass(Registry, cls))
        self.assertTrue(issubclass(cls, Registry))
        self.assertTrue(issubclass(cls, cls))

    def test_representation(self):
        cls = LazyClass('registry.base', 'Registry')
        self.assertEqual(repr(cls), '<LazyClass: registry.base.Registry>')
        cls = LazyClass('registry.base', 'asdfg')
        self.assertEqual(repr(cls), '<LazyClass: registry.base.asdfg>')


class LazyModelTest(test.SimpleTestCase):

    def test_lazy_loading(self):
        model = LazyModel('registry', 'asdfg')
        with self.assertRaises(MissingModelError):
            model._meta
        with self.assertRaises(MissingModelError):
            model._meta = None
        with self.assertRaises(MissingModelError):
            del model._meta

    def test_class(self):
        model = LazyModel('registry', 'Entry')
        from yepes.apps.registry.abstract_models import AbstractEntry
        from yepes.apps.registry.models import Entry
        self.assertEqual(model.__class__, AbstractEntry.__class__)
        self.assertEqual(model.__class__, Entry.__class__)

    def test_call(self):
        model = LazyModel('registry', 'Entry')
        from yepes.apps.registry.abstract_models import AbstractEntry
        from yepes.apps.registry.models import Entry
        self.assertIsInstance(model(), AbstractEntry)
        self.assertIsInstance(model(), Entry)
        self.assertIsInstance(model(), model)

    def test_instance_check(self):
        model = LazyModel('registry', 'Entry')
        from yepes.apps.registry.models import Entry
        self.assertIsInstance(Entry(), model)
        self.assertIsInstance(model(), model)

    @unittest.expectedFailure
    def test_subclass_check(self):
        model = LazyModel('registry', 'Entry')
        from yepes.apps.registry.abstract_models import AbstractEntry
        from yepes.apps.registry.models import Entry
        self.assertFalse(issubclass(AbstractEntry, Entry))
        self.assertFalse(issubclass(AbstractEntry, model))
        self.assertTrue(issubclass(Entry, Entry))
        self.assertTrue(issubclass(Entry, model))
        self.assertTrue(issubclass(model, Entry))
        self.assertTrue(issubclass(model, model))

    def test_representation(self):
        model = LazyModel('registry', 'Entry')
        self.assertEqual(repr(model), '<LazyModel: registry.Entry>')
        model = LazyModel('registry', 'asdfg')
        self.assertEqual(repr(model), '<LazyModel: registry.asdfg>')


class LazyModelManagerTest(test.SimpleTestCase):

    def test_lazy_loading(self):
        manager = LazyModelManager('registry', 'asdfg')
        with self.assertRaises(MissingModelError):
            manager.abstract
        with self.assertRaises(MissingModelError):
            manager.abstract = None
        with self.assertRaises(MissingModelError):
            del manager.abstract

    def test_class(self):
        manager = LazyModelManager('registry', 'Entry')
        from django.db.models import Manager
        from django.contrib.sites.managers import CurrentSiteManager
        from yepes.apps.registry.models import Entry
        EntryManager = Entry._default_manager

        self.assertNotEqual(manager.__class__, Manager)
        self.assertIsInstance(manager, Manager)
        self.assertEqual(manager.__class__, CurrentSiteManager)
        self.assertIsInstance(manager, CurrentSiteManager)
        self.assertEqual(manager.__class__, EntryManager.__class__)
        self.assertIsInstance(manager, EntryManager.__class__)

    def test_attributes(self):
        manager = LazyModelManager('registry', 'Entry')
        from yepes.apps.registry.models import Entry
        EntryManager = Entry._default_manager

        self.assertEqual(manager.creation_counter, EntryManager.creation_counter)
        self.assertEqual(manager.model, EntryManager.model)
        self.assertEqual(manager.db, EntryManager.db)

    def test_indicate_manager(self):
        manager = LazyModelManager('registry', 'Entry', 'all_objects')
        from django.db.models import Manager
        from django.contrib.sites.managers import CurrentSiteManager
        from yepes.apps.registry.models import Entry

        self.assertEqual(manager.__class__, Manager)
        self.assertIsInstance(manager, Manager)
        self.assertNotEqual(manager.__class__, CurrentSiteManager)
        self.assertNotIsInstance(manager, CurrentSiteManager)
        self.assertEqual(manager.__class__, Entry.all_objects.__class__)
        self.assertIsInstance(manager, Entry.all_objects.__class__)

        self.assertEqual(manager.creation_counter, Entry.all_objects.creation_counter)
        self.assertEqual(manager.model, Entry.all_objects.model)
        self.assertEqual(manager.db, Entry.all_objects.db)

    def test_representation(self):
        manager = LazyModelManager('registry', 'Entry')
        self.assertEqual(repr(manager), '<LazyModelManager: registry.Entry>')
        manager = LazyModelManager('registry', 'Entry', 'all_objects')
        self.assertEqual(repr(manager), '<LazyModelManager: registry.Entry.all_objects>')
        manager = LazyModelManager('registry', 'asdfg')
        self.assertEqual(repr(manager), '<LazyModelManager: registry.asdfg>')
        manager = LazyModelManager('registry', 'asdfg', 'all_objects')
        self.assertEqual(repr(manager), '<LazyModelManager: registry.asdfg.all_objects>')


class LazyModelObjectTest(test.SimpleTestCase):

    @classmethod
    def setUpClass(cls):
        from django.contrib.sites.models import Site
        from yepes.apps.registry.models import Entry
        Entry.objects.create(
            site=Site.objects.get_current(),
            key='KEY',
            value='VALUE')

    @classmethod
    def tearDownClass(cls):
        from yepes.apps.registry.models import Entry
        Entry.objects.filter(key='KEY').delete()

    def test_lazy_loading(self):
        from yepes.apps.registry.models import Entry
        lazy_obj = LazyModelObject(Entry, key='asdfg')
        with self.assertRaises(Entry.DoesNotExist):
            lazy_obj.key

        lazy_obj = LazyModelObject('registry.Entry', key='asdfg')
        with self.assertRaises(Entry.DoesNotExist):
            lazy_obj.key = 'hjklñ'

        lazy_obj = LazyModelObject('registry.Entry', 'all_objects', key='asdfg')
        with self.assertRaises(Entry.DoesNotExist):
            del lazy_obj.key

    def test_class(self):
        from yepes.apps.registry.models import Entry
        obj = Entry.objects.get(key='KEY')
        lazy_obj = LazyModelObject(Entry, key='KEY')
        self.assertEqual(lazy_obj.__class__, obj.__class__)
        self.assertEqual(lazy_obj.__class__, Entry)
        self.assertIsInstance(lazy_obj, obj.__class__)
        self.assertIsInstance(lazy_obj, Entry)

    def test_attributes(self):
        from yepes.apps.registry.models import Entry
        obj = Entry.objects.get(key='KEY')
        lazy_obj = LazyModelObject(Entry, key='KEY')
        self.assertEqual(lazy_obj.pk, obj.pk)
        self.assertEqual(lazy_obj.site, obj.site)
        self.assertEqual(lazy_obj.key, obj.key)
        self.assertEqual(lazy_obj.value, obj.value)

    def test_equal(self):
        from yepes.apps.registry.models import Entry
        obj = Entry.objects.get(key='KEY')
        lazy_obj = LazyModelObject(Entry, key='KEY')
        self.assertEqual(lazy_obj, obj)
        self.assertEqual(lazy_obj, obj)
        self.assertEqual(obj, lazy_obj)

    def test_not_equal(self):
        from yepes.apps.registry.models import Entry
        obj = Entry.objects.get(key='KEY')
        lazy_obj = LazyModelObject(Entry, key='KEY')
        self.assertFalse(lazy_obj != obj)
        self.assertFalse(lazy_obj != obj)
        self.assertFalse(obj != lazy_obj)

    def test_hash(self):
        from yepes.apps.registry.models import Entry
        obj = Entry.objects.get(key='KEY')
        lazy_obj = LazyModelObject(Entry, key='KEY')
        self.assertEqual(hash(lazy_obj), hash(obj))
        self.assertEqual(hash(obj), hash(lazy_obj))
        self.assertIn(lazy_obj, {obj})
        self.assertIn(obj, {lazy_obj})

    def test_string(self):
        from yepes.apps.registry.models import Entry
        obj = Entry.objects.get(key='KEY')
        lazy_obj = LazyModelObject(Entry, key='KEY')
        self.assertEqual(str(lazy_obj), str(obj))
        self.assertEqual(str(obj), str(lazy_obj))

    def test_representation(self):
        from yepes.apps.registry.models import Entry
        obj = Entry.objects.get(key='KEY')
        lazy_obj = LazyModelObject(Entry, key='KEY')
        self.assertNotEqual(repr(lazy_obj), repr(obj))
        self.assertEqual(repr(lazy_obj), '<LazyModelObject: {0}>'.format(obj))

