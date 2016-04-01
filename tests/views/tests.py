# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from django import test
from django.core.urlresolvers import reverse
from django.http import Http404
from django.test.utils import override_settings
from django.utils.encoding import force_text

from .models import Article


@override_settings(ROOT_URLCONF='views.urls')
class DetailViewTest(test.TestCase):

    def setUp(self):
        super(DetailViewTest, self).setUp()
        self.article = Article.objects.create(title='Django for Dummies')

    def test_slug_history(self):
        with self.assertNumQueries(1):
            resp = self.client.get('/django-for-dummies.html')
        self.assertEqual('django-for-dummies', force_text(resp.content))

        with self.assertNumQueries(2):
            resp = self.client.get('/the-django-book.html')
        self.assertEqual(404, resp.status_code)

        self.article.name = 'The Django Book'
        self.article.slug = 'the-django-book'
        self.article.save()

        with self.assertNumQueries(2):
            resp = self.client.get('/django-for-dummies.html')
        self.assertEqual(301, resp.status_code)
        self.assertEqual('http://testserver/the-django-book.html', resp.url)

        with self.assertNumQueries(1):
            resp = self.client.get('/the-django-book.html')
        self.assertEqual('the-django-book', force_text(resp.content))

        new_article = Article.objects.create(title='Django for Dummies')

        with self.assertNumQueries(1):
            resp = self.client.get('/django-for-dummies.html')
        self.assertEqual('django-for-dummies', force_text(resp.content))

        with self.assertNumQueries(1):
            resp = self.client.get('/the-django-book.html')
        self.assertEqual('the-django-book', force_text(resp.content))

