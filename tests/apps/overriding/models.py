# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from django.db import models


class Article(models.Model):

    title = models.CharField(
            max_length=255)
    extract = models.TextField(
            blank=True)
    content = models.TextField(
            blank=True)

    author = models.ForeignKey(
            'overridable.Author',
            related_name='articles')

    class Meta:
        ordering = ['title']

    def __str__(self):
        return self.title

    __unicode__ = __str__

