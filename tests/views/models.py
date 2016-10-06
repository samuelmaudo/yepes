# -*- coding:utf-8 -*-

from django.core.urlresolvers import reverse
from django.db import models
from django.utils.encoding import python_2_unicode_compatible

from yepes.model_mixins import Slugged


@python_2_unicode_compatible
class Article(Slugged):

    title = models.CharField(max_length=255)
    content = models.TextField(blank=True)

    class Meta:
        ordering = ['title']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('article_detail', kwargs={'slug': self.slug})


@python_2_unicode_compatible
class Artist(models.Model):

    name = models.CharField(max_length=100)

    class Meta:
        ordering = ['name']
        verbose_name = 'professional artist'
        verbose_name_plural = 'professional artists'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('artist_detail', kwargs={'pk': self.id})


@python_2_unicode_compatible
class Author(models.Model):

    name = models.CharField(max_length=100)
    slug = models.SlugField()

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


@python_2_unicode_compatible
class Book(models.Model):

    name = models.CharField(max_length=300)
    slug = models.SlugField()
    pages = models.IntegerField()
    authors = models.ManyToManyField(Author)
    pubdate = models.DateField()

    objects = models.Manager()

    class Meta:
        ordering = ['-pubdate']

    def __str__(self):
        return self.name


class BookSigning(models.Model):

    event_date = models.DateTimeField()


class Page(models.Model):

    content = models.TextField()
    template = models.CharField(max_length=300)

