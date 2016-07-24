# -*- coding:utf-8 -*-

from django.db import models
from django.utils.translation import ugettext_lazy as _

from yepes.contrib.registry.abstract_models import BaseEntry


class Entry(BaseEntry):

    value = models.CharField(
            max_length=255,
            blank=True,
            null=True,
            verbose_name=_('Value'))

    class Meta:
        unique_together = ('site', 'key')
        verbose_name = _('Entry')
        verbose_name_plural = _('Entries')


class LongEntry(BaseEntry):

    value = models.TextField(
            blank=True,
            null=True,
            verbose_name=_('Value'))

    class Meta:
        unique_together = ('site', 'key')
        verbose_name = _('Long Entry')
        verbose_name_plural = _('Long Entries')

