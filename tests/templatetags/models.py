# -*- coding:utf-8 -*-

from django.db import models
from django.utils.encoding import python_2_unicode_compatible

from yepes.model_mixins import Nestable, ParentForeignKey


@python_2_unicode_compatible
class Category(Nestable):

    parent = ParentForeignKey(
            'self',
            blank=True,
            null=True,
            on_delete=models.CASCADE,
            related_name='children')

    name = models.CharField(
            max_length=63)

    class MPTTMeta:
        order_insertion_by = ['name']

    def __str__(self):
        if self.parent is not None:
            return '{0} > {1}'.format(self.parent, self.name)
        else:
            return self.name
