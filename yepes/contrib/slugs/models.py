# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _

from yepes.contrib.slugs.managers import SlugHistoryManager


@python_2_unicode_compatible
class SlugHistory(models.Model):

    slug = models.CharField(
            db_index=True,
            editable=False,
            max_length=255,
            verbose_name=_('Slug'))

    object_type = models.ForeignKey(
            ContentType,
            editable=False,
            on_delete=models.CASCADE,
            verbose_name=_('Object Type'))
    object_id = models.PositiveIntegerField(
            db_index=True,
            editable=False,
            verbose_name=_('Object ID'))
    object = GenericForeignKey(
            'object_type',
            'object_id')

    objects = SlugHistoryManager()

    class Meta:
        ordering = ['-pk']
        verbose_name = _('Slug Entry')
        verbose_name_plural = _('Slug Entries')

    def __str__(self):
        return self.slug

