# -*- coding:utf-8 -*-

from __future__ import unicode_literals

import unittest
import warnings

from django import test

from yepes.cache import MintCache, LookupTable

from .models import Tax


class LookupTableTest(test.TestCase):

    def setUp(self):
        self.standard = Tax.objects.create(name='Standard VAT', rate=20.0)
        self.reduced = Tax.objects.create(name='Reduced VAT', rate=5.0)
        self.zero = Tax.objects.create(name='Zero VAT', rate=0.0)

    def test_all(self):
        with self.assertNumQueries(1):
            self.assertEqual(list(Tax.cache.all()),
                             [self.standard, self.reduced, self.zero])
        with self.assertNumQueries(0):
            self.assertEqual(list(Tax.cache.all()),
                             [self.standard, self.reduced, self.zero])

    def test_clear(self):
        with self.assertNumQueries(1):
            self.assertEqual(list(Tax.cache.all()),
                             [self.standard, self.reduced, self.zero])
        with self.assertNumQueries(0):
            Tax.cache.clear()
        with self.assertNumQueries(1):
            self.assertEqual(list(Tax.cache.all()),
                             [self.standard, self.reduced, self.zero])

    def test_exists(self):
        exists = Tax.cache.exists
        with self.assertNumQueries(1):
            self.assertTrue(exists(self.standard.pk))
        with self.assertNumQueries(0):
            self.assertTrue(exists(name=self.standard.name))
            self.assertFalse(exists(0))
            self.assertFalse(exists(name='Another Tax'))

    def test_exists_many(self):
        exists_many = Tax.cache.exists_many
        with self.assertNumQueries(1):
            self.assertTrue(exists_many([self.standard.pk, self.reduced.pk]))
        with self.assertNumQueries(0):
            self.assertTrue(exists_many(name=[self.standard.name, self.reduced.name]))
            self.assertFalse(exists_many([self.standard.pk, 0]))
            self.assertFalse(exists_many(name=['Another Tax', self.standard.name]))

    def test_get(self):
        get = Tax.cache.get
        with self.assertNumQueries(1):
            self.assertEqual(get(self.standard.pk), self.standard)
        with self.assertNumQueries(0):
            self.assertEqual(get(name=self.standard.name), self.standard)
            self.assertEqual(get(0), None)
            self.assertEqual(get(name='Another Tax'), None)

    def test_get_many(self):
        get_many = Tax.cache.get_many
        with self.assertNumQueries(1):
            self.assertEqual(get_many([self.standard.pk, self.reduced.pk]),
                             [self.standard, self.reduced])
        with self.assertNumQueries(0):
            self.assertEqual(get_many(name=[self.standard.name, self.reduced.name]),
                             [self.standard, self.reduced])
            self.assertEqual(get_many([self.standard.pk, 0]),
                             [self.standard, None])
            self.assertEqual(get_many(name=['Another Tax', self.standard.name]),
                             [None, self.standard])

    def test_create(self):
        create = Tax.cache.create
        get = Tax.cache.get
        with self.assertNumQueries(1):
            general = create(name='IVA General', rate=21.0)
        with self.assertNumQueries(1):
            self.assertEqual(get(name='IVA General'), general)
        with self.assertNumQueries(1):
            reducido = create(name='IVA Reducido', rate=10.0)
        with self.assertNumQueries(0):
            self.assertEqual(get(name='IVA Reducido'), reducido)

    def test_get_or_create(self):
        get_or_create = Tax.cache.get_or_create
        with self.assertNumQueries(2):
            general_1, created = get_or_create(name='IVA General', defaults={'rate': 21.0})
        self.assertTrue(created)
        with self.assertNumQueries(0):
            general_2, created = get_or_create(name='IVA General')
        self.assertFalse(created)
        self.assertEqual(general_1, general_2)

