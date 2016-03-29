# -*- coding:utf-8 -*-

from django.db import models

from yepes import fields
from yepes.managers import (
    NestableManager,
    SluggedManager,
)
from yepes.model_mixins import (
    Activatable,
    Displayable,
    Enableable,
    Illustrated,
    Logged,
    MetaData,
    Multilingual,
    Nestable, ParentForeignKey,
    Orderable,
    Slugged,
)


class Article(Displayable, Logged):

    title = models.CharField(
            max_length=255)
    content = models.TextField(
            blank=True)

    search_fields = {'title': 3, 'content': 1}

    class Meta:
        ordering = ['title']

    def __str__(self):
        return self.title

    __unicode__ = __str__

    def get_absolute_url(self):
        return '/articles/{0}.html'.format(self.slug)


class Book(Multilingual):

    isbn = models.IntegerField()

    class Meta:
        translation = 'BookTranslation'
        multilingual = ['title', 'description']

    def __str__(self):
        return str(self.isbn)

    __unicode__ = __str__


class BookTranslation(models.Model):

    language = models.ForeignKey(
            'Language',
            related_name='book_translations')
    title = models.CharField(
            max_length=32)
    description = models.TextField(
            blank=True)
    model = models.ForeignKey(
            'Book',
            related_name='translations')

    def __str__(self):
        return self.title

    __unicode__ = __str__


class CategoryManager(NestableManager, SluggedManager):
    pass


class Category(Nestable, Slugged):

    parent = ParentForeignKey(
            'self',
            blank=True,
            null=True,
            related_name='children')
    name = models.CharField(
            unique=True,
            max_length=63)

    objects = CategoryManager()

    class MPTTMeta:
        order_insertion_by = ['name']

    def __str__(self):
        return self.name

    __unicode__ = __str__

    def get_absolute_url(self):
        return '/categories/{0}.html'.format(self.slug)


class Image(Orderable, Illustrated):

    article = models.ForeignKey(
            'Article',
            related_name='images')

    class Meta:
        folder_name = 'article_images'
        order_with_respect_to = 'article'


class Language(Orderable):

    tag = models.CharField(
            max_length=5)
    name = models.CharField(
            max_length=16)

    def __str__(self):
        return self.name

    __unicode__ = __str__


class Product(Displayable, Illustrated, Logged):

    name = models.CharField(
            max_length=64)
    description = models.TextField(
            blank=True)

    search_fields = {'variants__sku': 9, 'name': 3, 'description': 1}

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    __unicode__ = __str__

    def get_absolute_url(self):
        return '/products/{0}.html'.format(self.slug)


class ProductVariant(Orderable):

    product = models.ForeignKey(
            'Product',
            related_name='variants')
    sku = models.CharField(
            max_length=32,
            unique=True)
    name = models.CharField(
            max_length=128,
            unique=True)

    class Meta:
        order_with_respect_to = 'product'

    def __str__(self):
        return self.name

    __unicode__ = __str__


class RichArticle(Displayable, Logged):

    name = models.CharField(
            blank=True,
            max_length=255)
    headline = models.CharField(
            blank=True,
            max_length=255)
    title = models.CharField(
            blank=True,
            max_length=255)

    content = fields.RichTextField(
            blank=True)
    description = fields.RichTextField(
            blank=True)
    excerpt = fields.RichTextField(
            blank=True)

    search_fields = {'title': 3, 'content': 1}

    class Meta:
        ordering = ['title']

    def __str__(self):
        return self.title

    __unicode__ = __str__

    def get_absolute_url(self):
        return '/articles/{0}.html'.format(self.slug)


class Volcano(Activatable):

    name = models.CharField(
            max_length=255)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    __unicode__ = __str__

