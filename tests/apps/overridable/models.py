# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from django.db import models


class Article(models.Model):

    title = models.CharField(
            max_length=255)
    content = models.TextField(
            blank=True)

    author = models.ForeignKey(
            'overridable.Author',
            on_delete=models.CASCADE,
            related_name='+')

    class Meta:
        ordering = ['title']

    def __str__(self):
        return self.title

    __unicode__ = __str__


class Author(models.Model):

    name = models.CharField(
            max_length=127)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    __unicode__ = __str__

