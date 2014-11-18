# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from django.db import models


class Article(models.Model):

    title = models.CharField(
            max_length=255)
    slug = models.SlugField(
            max_length=255)
    content = models.TextField(
            blank=True)

    def __str__(self):
        return self.title

    __unicode__ = __str__

    def get_absolute_url(self):
        return '/{0}-{1}/'.format(self.slug, self.pk)

