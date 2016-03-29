# -*- coding:utf-8 -*-

from django.db import models

from yepes.model_mixins import Slugged


class Article(Slugged):

    title = models.CharField(
            max_length=255)
    content = models.TextField(
            blank=True)

    class Meta:
        ordering = ['title']

    def __str__(self):
        return self.title

    __unicode__ = __str__

    def get_absolute_url(self):
        return '/{0}.html'.format(self.slug)

