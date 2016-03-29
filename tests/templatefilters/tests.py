# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from collections import OrderedDict

from django import test
from django.db import models
from django.utils.six.moves import range

from yepes import defaultfilters as filters
from yepes.model_mixins import Displayable


class DefaultFiltersTest(test.SimpleTestCase):

    def test_endswith(self):
        self.assertTrue(filters.endswith('bilbo', 'bo'))
        self.assertFalse(filters.endswith('bilbo', 'do'))
        self.assertTrue(filters.endswith(None, 'ne'))
        self.assertTrue(filters.endswith(True, 'ue'))
        self.assertFalse(filters.endswith(False, 'ue'))
        self.assertTrue(filters.endswith(100, '00'))
        self.assertFalse(filters.endswith(100, '23'))

    def test_first(self):
        self.assertEqual(filters.first('abc'), 'a')
        self.assertEqual(filters.first(tuple('abc')), 'a')
        self.assertEqual(filters.first(list('abc')), 'a')
        self.assertEqual(filters.first(iter('abc')), 'a')
        self.assertEqual(filters.first(OrderedDict([('a', 1), ('b', 2), ('c', 3)])), 'a')
        self.assertEqual(filters.first(''), None)
        self.assertEqual(filters.first(tuple('')), None)
        self.assertEqual(filters.first(list('')), None)
        self.assertEqual(filters.first(iter('')), None)
        self.assertEqual(filters.first(OrderedDict()), None)
        self.assertEqual(filters.first(None), None)
        self.assertEqual(filters.first(False), None)
        self.assertEqual(filters.first(0), None)

    def test_get(self):
        class Article(Displayable):
            name = models.CharField(max_length=255)
            text = models.TextField(blank=True)
        self.assertEqual(filters.get(Article(), 'name'), '')
        self.assertEqual(filters.get(Article(name='The Hobbit'), 'name'), 'The Hobbit')
        self.assertEqual(filters.get({}, 'name'), None)
        self.assertEqual(filters.get({'name': 'The Hobbit'}, 'name'), 'The Hobbit')
        self.assertEqual(filters.get(None, 'name'), None)
        self.assertEqual(filters.get('', 'name'), None)
        self.assertEqual(filters.get(0, 'name'), None)

    def test_last(self):
        self.assertEqual(filters.last('abc'), 'c')
        self.assertEqual(filters.last(tuple('abc')), 'c')
        self.assertEqual(filters.last(list('abc')), 'c')
        self.assertEqual(filters.last(iter('abc')), 'c')
        self.assertEqual(filters.last(OrderedDict([('a', 1), ('b', 2), ('c', 3)])), 'c')
        self.assertEqual(filters.last(''), None)
        self.assertEqual(filters.last(tuple('')), None)
        self.assertEqual(filters.last(list('')), None)
        self.assertEqual(filters.last(iter('')), None)
        self.assertEqual(filters.last(OrderedDict()), None)
        self.assertEqual(filters.last(None), None)
        self.assertEqual(filters.last(False), None)
        self.assertEqual(filters.last(0), None)

    def test_pk(self):
        class Article(Displayable):
            name = models.CharField(max_length=255)
            text = models.TextField(blank=True)
        self.assertIsNone(filters.pk(Article()))
        self.assertEqual(filters.pk(Article(id=1)), 1)
        self.assertEqual(filters.pk(Article(pk=2)), 2)
        self.assertIsNone(filters.pk(None))
        self.assertIsNone(filters.pk(''))
        self.assertIsNone(filters.pk(0))

    def test_roundlist(self):
        self.assertEqual(
            [0, 1, 2, None, None],
            filters.roundlist([0, 1, 2], 5),
        )
        self.assertEqual(
            [0, 1, 2, 3, 4, 5, 6, None, None, None],
            filters.roundlist((0, 1, 2, 3, 4, 5, 6), 5),
        )
        self.assertEqual(
            [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
            filters.roundlist(range(10), 5),
        )
        self.assertEqual(
            [],
            filters.roundlist('', None),
        )
        self.assertEqual(
            [None, None, None, None, None],
            filters.roundlist('', 5),
        )

    def test_startswith(self):
        self.assertTrue(filters.startswith('frodo', 'fro'))
        self.assertFalse(filters.startswith('frodo', 'bil'))
        self.assertTrue(filters.startswith(None, 'No'))
        self.assertTrue(filters.startswith(True, 'Tr'))
        self.assertFalse(filters.startswith(False, 'Tr'))
        self.assertTrue(filters.startswith(100, '10'))
        self.assertFalse(filters.startswith(100, '12'))

    def test_strip(self):
        self.assertEqual(filters.strip('bilbo'), 'bilbo')
        self.assertEqual(filters.strip('\tbilbo  \n'), 'bilbo')
        self.assertEqual(filters.strip('bilbo', 'bo'), 'il')
        self.assertEqual(filters.strip(None), 'None')
        self.assertEqual(filters.strip(True), 'True')
        self.assertEqual(filters.strip(False, 'Fe'), 'als')
        self.assertEqual(filters.strip(100), '100')
        self.assertEqual(filters.strip(100, '0'), '1')

    def test_toascii(self):
        self.assertEqual(filters.toascii('&#60;bilbo&gt;'), '<bilbo>')
        self.assertEqual(filters.toascii('100,00 &euro;'), '100,00 EU')
        self.assertEqual(filters.toascii('&#2384;&#x950;'), 'AUMAUM')

    def test_toentities(self):
        self.assertEqual(filters.toentities('<bilbo>'), '&lt;bilbo&gt;')
        self.assertEqual(filters.toentities('100,00 €'), '100,00 &euro;')
        self.assertEqual(filters.toentities('ॐॐ'), '&#2384;&#2384;')

    def test_tounicode(self):
        self.assertEqual(filters.tounicode('&#60;bilbo&gt;'), '<bilbo>')
        self.assertEqual(filters.tounicode('100,00 &euro;'), '100,00 €')
        self.assertEqual(filters.tounicode('&#2384;&#x950;'), 'ॐॐ')

