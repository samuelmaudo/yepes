# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from django.contrib.sites.models import Site
from django.contrib.sites.managers import CurrentSiteManager
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _


@python_2_unicode_compatible
class BaseEntry(models.Model):

    site = models.ForeignKey(
            Site,
            verbose_name=_('Site'))
    key = models.CharField(
            max_length=63,
            verbose_name=_('Key'))

    objects = CurrentSiteManager()
    all_objects = models.Manager()

    class Meta:
        abstract = True

    def __str__(self):
        return self.key

    @staticmethod
    def autocomplete_search_fields():
        return ('key__icontains', )

    def natural_key(self):
        return (self.key, )


class AbstractEntry(BaseEntry):

    value = models.CharField(
            max_length=255,
            blank=True,
            null=True,
            verbose_name=_('Value'))

    class Meta:
        abstract = True
        unique_together = ('site', 'key')
        verbose_name = _('Entry')
        verbose_name_plural = _('Entries')


class AbstractLongEntry(BaseEntry):

    value = models.TextField(
            blank=True,
            null=True,
            verbose_name=_('Value'))

    class Meta:
        abstract = True
        unique_together = ('site', 'key')
        verbose_name = _('Long Entry')
        verbose_name_plural = _('Long Entries')

