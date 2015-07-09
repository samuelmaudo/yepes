# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from wand.image import FILTER_TYPES

from django.db import models
from django.utils import timezone
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _

from yepes import fields
from yepes.cache import LookupTable
from yepes.model_mixins.logged import Logged


@python_2_unicode_compatible
class AbstractConfiguration(Logged):

    FILTER_CHOICES = tuple(
        (type, type)
        for type
        in FILTER_TYPES
    )
    FORMAT_CHOICES = (
        ('GIF', 'GIF'),
        ('JPEG', 'JPEG'),
        ('PNG', 'PNG'),
        ('WEBP', 'WEBP'),
    )
    key = fields.IdentifierField(
            max_length=63,
            unique=True,
            verbose_name=_('Key'))

    width = fields.IntegerField(
            min_value=0,
            verbose_name=_('Width'))
    height = fields.IntegerField(
            min_value=0,
            verbose_name=_('Height'))

    filter = fields.CharField(
            choices=FILTER_CHOICES,
            default='undefined',
            max_length=15,
            verbose_name=_('Filter'))
    blur = fields.FloatField(
            default=1.0,
            min_value=0.0,
            verbose_name=_('Blur'))

    format = fields.CharField(
            choices=FORMAT_CHOICES,
            default='JPEG',
            max_length=15,
            verbose_name=_('Format'))
    quality = fields.IntegerField(
            default=85,
            max_value=100,
            min_value=1,
            verbose_name=_('Quality'))

    cache = LookupTable(['key'])

    class Meta:
        abstract = True
        ordering = ['key']
        verbose_name = _('Thumbnail Configuration')
        verbose_name_plural = _('Configurations')

    def __str__(self):
        return self.key

    @staticmethod
    def autocomplete_search_fields():
        return ('host__icontains', )


@python_2_unicode_compatible
class AbstractSource(models.Model):

    name = fields.CharField(
            unique=True,
            max_length=255,
            verbose_name=_('Name'))
    last_modified = models.DateTimeField(
            default=timezone.now,
            verbose_name=_('Last Modified'))

    class Meta:
        abstract = True
        ordering = ['name']
        verbose_name = _('Source')
        verbose_name_plural = _('Sources')

    def __str__(self):
        return self.name


@python_2_unicode_compatible
class AbstractThumbnail(models.Model):

    source = models.ForeignKey(
            'Source',
            related_name='thumbnails',
            verbose_name=_('Source'))

    name = fields.CharField(
            max_length=255,
            verbose_name=_('Name'))
    last_modified = models.DateTimeField(
            default=timezone.now,
            verbose_name=_('Last Modified'))

    class Meta:
        abstract = True
        ordering = ['source', 'name']
        unique_together = [('source', 'name')]
        verbose_name = _('Thumbnail')
        verbose_name_plural = _('Thumbnails')

    def __str__(self):
        return self.name

