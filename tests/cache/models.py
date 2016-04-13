# -*- coding:utf-8 -*-

from django.db import models

from yepes.cache import LookupTable


class Tax(models.Model):

    name = models.CharField(max_length=63)
    rate = models.FloatField()

    cache = LookupTable(['name'])

    class Meta:
        ordering = ['pk']

    def __str__(self):
        return self.name

    __unicode__ = __str__

