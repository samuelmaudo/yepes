# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils import translation
from django.utils.translation import ugettext_lazy as _

from yepes.conf import settings


@python_2_unicode_compatible
class Standard(models.Model):

    name = models.CharField(
            unique=True,
            max_length=127,
            verbose_name=_('Native Name'))
    name_de = models.CharField(
            blank=True,
            db_index=True,
            max_length=127,
            verbose_name=_('German Name'))
    name_en = models.CharField(
            blank=True,
            db_index=True,
            max_length=127,
            verbose_name=_('English Name'))
    name_es = models.CharField(
            blank=True,
            db_index=True,
            max_length=127,
            verbose_name=_('Spanish Name'))
    name_fr = models.CharField(
            blank=True,
            db_index=True,
            max_length=127,
            verbose_name=_('French Name'))
    name_pt = models.CharField(
            blank=True,
            db_index=True,
            max_length=127,
            verbose_name=_('Portuguese Name'))
    name_ru = models.CharField(
            blank=True,
            db_index=True,
            max_length=127,
            verbose_name=_('Russian Name'))
    name_zh = models.CharField(
            blank=True,
            db_index=True,
            max_length=127,
            verbose_name=_('Chinese Name'))

    class Meta:
        abstract = True

    def __str__(self):
        if settings.STANDARDS_DEFAULT_TRANSLATION == 'native':
            return self.name
        if settings.STANDARDS_DEFAULT_TRANSLATION == 'locale':
            language = translation.get_language()
        else:
            language = settings.STANDARDS_DEFAULT_TRANSLATION
        try:
            return getattr(self, 'name_{0}'.format(language[:2]))
        except AttributeError:
            fallback = settings.STANDARDS_FALLBACK_TRANSLATION
            return getattr(self, 'name_{0}'.format(fallback))

