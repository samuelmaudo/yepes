# -*- coding:utf-8 -*-

from __future__ import unicode_literals

import datetime

from django import test
from django.core.exceptions import ImproperlyConfigured
from django.core.urlresolvers import reverse
from django.http import Http404
from django.test.utils import override_settings
from django.utils.encoding import force_str, force_text
from django.views.generic.base import View

from .models import Article, Artist, Author, Book, Page


@override_settings(ROOT_URLCONF='views.urls')
class ListViewTests(test.TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.artist1 = Artist.objects.create(
            name='Rene Magritte'
        )
        cls.author1 = Author.objects.create(
            name='Roberto Bolaño',
            slug='roberto-bolano'
        )
        cls.author2 = Author.objects.create(
            name='Scott Rosenberg',
            slug='scott-rosenberg'
        )
        cls.book1 = Book.objects.create(
            name='2066',
            slug='2066',
            pages=800,
            pubdate=datetime.date(2008, 10, 1)
        )
        cls.book1.authors.add(cls.author1)
        cls.book2 = Book.objects.create(
            name='Dreaming in Code',
            slug='dreaming-in-code',
            pages=300,
            pubdate=datetime.date(2006, 5, 1)
        )
        cls.page1 = Page.objects.create(
            content='I was once bitten by a moose.',
            template='views_tests/page_template.html'
        )

    def _make_authors(self, n):
        Author.objects.all().delete()
        for i in range(n):
            Author.objects.create(name='Author %02i' % i, slug='a%s' % i)

    def test_items(self):
        res = self.client.get('/list/dict/')
        self.assertEqual(res.status_code, 200)
        self.assertTemplateUsed(res, 'views_tests/list.html')
        self.assertEqual(res.context['object_list'][0]['first'], 'John')

    def test_queryset(self):
        res = self.client.get('/list/authors/')
        self.assertEqual(res.status_code, 200)
        self.assertTemplateUsed(res, 'views_tests/author_list.html')
        self.assertEqual(list(res.context['object_list']), list(Author.objects.all()))
        self.assertIsInstance(res.context['view'], View)
        self.assertIs(res.context['author_list'], res.context['object_list'])
        self.assertEqual(res.context['query'].num_pages, 1)
        self.assertEqual(res.context['page_obj'].number, 1)
        self.assertFalse(res.context['is_paginated'])

    def test_paginated_queryset(self):
        self._make_authors(100)
        res = self.client.get('/list/authors/paginated/')
        self.assertEqual(res.status_code, 200)
        self.assertTemplateUsed(res, 'views_tests/author_list.html')
        self.assertEqual(len(res.context['object_list']), 30)
        self.assertIs(res.context['author_list'], res.context['object_list'])
        self.assertTrue(res.context['is_paginated'])
        self.assertEqual(res.context['query'].num_pages, 4)
        self.assertEqual(res.context['page_obj'].number, 1)
        self.assertEqual(res.context['author_list'][0].name, 'Author 00')
        self.assertEqual(list(res.context['author_list'])[-1].name, 'Author 29')

    def test_paginated_queryset_shortdata(self):
        # Test that short datasets ALSO result in a paginated view.
        res = self.client.get('/list/authors/paginated/')
        self.assertEqual(res.status_code, 200)
        self.assertTemplateUsed(res, 'views_tests/author_list.html')
        self.assertEqual(list(res.context['object_list']), list(Author.objects.all()))
        self.assertIs(res.context['author_list'], res.context['object_list'])
        self.assertEqual(res.context['query'].num_pages, 1)
        self.assertEqual(res.context['page_obj'].number, 1)
        self.assertFalse(res.context['is_paginated'])

    def test_paginated_get_page_by_query_string(self):
        self._make_authors(100)
        res = self.client.get('/list/authors/paginated/', {'page': '2'})
        self.assertEqual(res.status_code, 200)
        self.assertTemplateUsed(res, 'views_tests/author_list.html')
        self.assertEqual(len(res.context['object_list']), 30)
        self.assertIs(res.context['author_list'], res.context['object_list'])
        self.assertEqual(res.context['author_list'][0].name, 'Author 30')
        self.assertEqual(res.context['page_obj'].number, 2)

    def test_paginated_get_last_page_by_query_string(self):
        self._make_authors(100)
        res = self.client.get('/list/authors/paginated/', {'page': 'last'})
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.context['object_list']), 10)
        self.assertIs(res.context['author_list'], res.context['object_list'])
        self.assertEqual(res.context['author_list'][0].name, 'Author 90')
        self.assertEqual(res.context['page_obj'].number, 4)

    def test_paginated_page_out_of_range(self):
        self._make_authors(100)
        res = self.client.get('/list/authors/paginated/', {'page': '42'})
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.context['page_obj'].number, 1)

    def test_paginated_invalid_page(self):
        self._make_authors(100)
        res = self.client.get('/list/authors/paginated/?page=frog')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.context['page_obj'].number, 1)

    def test_paginated_custom_page_kwarg(self):
        self._make_authors(100)
        res = self.client.get('/list/authors/paginated/custom_page_kwarg/', {'pagina': '2'})
        self.assertEqual(res.status_code, 200)
        self.assertTemplateUsed(res, 'views_tests/author_list.html')
        self.assertEqual(len(res.context['object_list']), 30)
        self.assertIs(res.context['author_list'], res.context['object_list'])
        self.assertEqual(res.context['author_list'][0].name, 'Author 30')
        self.assertEqual(res.context['page_obj'].number, 2)

    def test_paginated_orphaned_queryset(self):
        self._make_authors(92)
        res = self.client.get('/list/authors/paginated-orphaned/')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.context['page_obj'].number, 1)
        res = self.client.get(
            '/list/authors/paginated-orphaned/', {'page': 'last'})
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.context['page_obj'].number, 3)
        res = self.client.get(
            '/list/authors/paginated-orphaned/', {'page': '3'})
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.context['page_obj'].number, 3)
        res = self.client.get(
            '/list/authors/paginated-orphaned/', {'page': '4'})
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.context['page_obj'].number, 1)

    def test_paginated_non_queryset(self):
        res = self.client.get('/list/dict/paginated/')

        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.context['object_list']), 1)

    def test_verbose_name(self):
        res = self.client.get('/list/artists/')
        self.assertEqual(res.status_code, 200)
        self.assertTemplateUsed(res, 'views_tests/list.html')
        self.assertEqual(list(res.context['object_list']), list(Artist.objects.all()))
        self.assertIs(res.context['artist_list'], res.context['object_list'])
        self.assertEqual(res.context['query'].num_pages, 1)
        self.assertEqual(res.context['page_obj'].number, 1)
        self.assertFalse(res.context['is_paginated'])

    def test_allow_empty_false(self):
        res = self.client.get('/list/authors/notempty/')
        self.assertEqual(res.status_code, 200)
        Author.objects.all().delete()
        res = self.client.get('/list/authors/notempty/')
        self.assertEqual(res.status_code, 404)

    def test_template_name(self):
        res = self.client.get('/list/authors/template_name/')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(list(res.context['object_list']), list(Author.objects.all()))
        self.assertIs(res.context['author_list'], res.context['object_list'])
        self.assertTemplateUsed(res, 'views_tests/list.html')

    def test_template_name_suffix(self):
        res = self.client.get('/list/authors/template_name_suffix/')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(list(res.context['object_list']), list(Author.objects.all()))
        self.assertIs(res.context['author_list'], res.context['object_list'])
        self.assertTemplateUsed(res, 'views_tests/author_objects.html')

    def test_context_object_name(self):
        res = self.client.get('/list/authors/context_object_name/')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(list(res.context['object_list']), list(Author.objects.all()))
        self.assertNotIn('authors', res.context)
        self.assertIs(res.context['author_list'], res.context['object_list'])
        self.assertTemplateUsed(res, 'views_tests/author_list.html')

    def test_duplicate_context_object_name(self):
        res = self.client.get('/list/authors/dupe_context_object_name/')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(list(res.context['object_list']), list(Author.objects.all()))
        self.assertNotIn('authors', res.context)
        self.assertNotIn('author_list', res.context)
        self.assertTemplateUsed(res, 'views_tests/author_list.html')

    def test_missing_items(self):
        with self.assertRaises(ImproperlyConfigured):
            self.client.get('/list/authors/invalid/')

    def test_paginated_list_view_does_not_load_entire_table(self):
        self._make_authors(3)
        # 1 query for authors
        with self.assertNumQueries(1):
            res = self.client.get('/list/authors/notempty/')
            self.assertEqual(len(res.context['object_list']), 3)
        # same as above + 1 query to test if authors exist and for pagination
        with self.assertNumQueries(2):
            res = self.client.get('/list/authors/notempty/paginated/')
            self.assertEqual(len(res.context['object_list']), 2)

    def test_explicitly_ordered_list_view(self):
        Book.objects.create(name="Zebras for Dummies", pages=800, pubdate=datetime.date(2006, 9, 1))
        res = self.client.get('/list/books/sorted/')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.context['object_list'][0].name, '2066')
        self.assertEqual(res.context['object_list'][1].name, 'Dreaming in Code')
        self.assertEqual(res.context['object_list'][2].name, 'Zebras for Dummies')

        res = self.client.get('/list/books/sortedbypagesandnamedesc/')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.context['object_list'][0].name, 'Dreaming in Code')
        self.assertEqual(res.context['object_list'][1].name, 'Zebras for Dummies')
        self.assertEqual(res.context['object_list'][2].name, '2066')

