# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from django.db import models
from django.utils.encoding import python_2_unicode_compatible


@python_2_unicode_compatible
class AbstractArticle(models.Model):

    title = models.CharField(
            max_length=255)
    content = models.TextField(
            blank=True)

    author = models.ForeignKey(
            'overridable.Author',
            on_delete=models.CASCADE,
            related_name='articles')

    class Meta:
        abstract = True
        ordering = ['title']

    def __str__(self):
        return self.title


@python_2_unicode_compatible
class AbstractAuthor(models.Model):

    name = models.CharField(
            max_length=127)

    class Meta:
        abstract = True
        ordering = ['name']

    def __str__(self):
        return self.name

