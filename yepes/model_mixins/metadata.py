# -*- coding:utf-8 -*-

from __future__ import unicode_literals

import collections
import operator
import re

from django.db import models
from django.utils import six
from django.utils.html import strip_tags
from django.utils.text import Truncator
from django.utils.translation import ugettext_lazy as _

from yepes import fields
from yepes.contrib.registry import registry

__all__ = ('MetaData', )

WORD_SEPARATORS_RE = re.compile(r'[\s\(\)\[\]\{\}\\\/\-+*%<>=.,:;&|#@¿?¡!]+')


class MetaData(models.Model):
    """
    Abstract model that provides meta data for content.
    """

    DEFAULT = None
    INDEX = True
    NOINDEX = False
    INDEX_CHOICES = (
        (DEFAULT, _('Default')),
        (INDEX, 'index'),
        (NOINDEX, 'noindex'),
    )
    meta_index = models.NullBooleanField(
            choices=INDEX_CHOICES,
            default=DEFAULT,
            verbose_name=_('Robots'))

    meta_title = fields.CharField(
            blank=True,
            max_length=127,
            verbose_name=_('Title'),
            help_text=_('Optional title to be used in the HTML title tag. '
                        'If left blank, the main title field will be used.'))
    meta_description = fields.TextField(
            blank=True,
            verbose_name=_('Description'),
            help_text=_('Optional description to be used in the description meta tag. '
                        'If left blank, the content field will be used.'))
    meta_keywords = fields.CommaSeparatedField(
            blank=True,
            verbose_name=_('Keywords'),
            help_text=_('Optional keywords to be used in the keywords meta tag. '
                        'If left blank, they will be extracted from the description.'))

    canonical_url = models.URLField(
            blank=True,
            max_length=255,
            verbose_name=_('Canonical URL'),
            help_text=_("Optional URL to be used in the canonical meta tag. "
                        "If left blank, the object's URL will be used."))

    class Meta:
        abstract = True

    def get_canonical_url(self):
        if self.canonical_url:
            return self.canonical_url
        elif hasattr(self, 'get_full_url'):
            return self.get_full_url()
        elif hasattr(self, 'get_absolute_url'):
            return self.get_absolute_url()
        else:
            return ''

    def get_default_meta_index(self):
        return True

    def get_meta_description(self, max_words=30, end_text='...'):
        if self.meta_description:
            description = self.meta_description
        else:
            description = ''
            fields = {fld.name: fld for fld in self._meta.get_fields()}
            for field_name in ('excerpt', 'description', 'content'):
                if field_name in fields:
                    field = fields[field_name]
                    if hasattr(field, 'html_field'):
                        field = field.html_field
                    description = getattr(self, field.name)
                    if description:
                        break
            else:
                for field in self._meta.get_fields():
                    if isinstance(field, models.TextField):
                        if hasattr(field, 'html_field'):
                            field = field.html_field
                        description = getattr(self, field.name)
                        if description:
                            break

        description = strip_tags(description)
        description = Truncator(description).words(max_words, end_text)
        return description

    def get_meta_index(self):
        if self.meta_index is None:
            return self.get_default_meta_index()
        else:
            return self.meta_index

    def get_meta_keywords(self, max_words=10):
        if self.meta_keywords:
            return ', '.join(self.meta_keywords[:max_words])

        words = []
        words.extend(WORD_SEPARATORS_RE.split(self.get_meta_title().lower()) * 2)
        words.extend(WORD_SEPARATORS_RE.split(self.get_meta_description().lower()))

        stop_words = registry['core:STOP_WORDS']

        # We do not use collections.Counter because we want to prioritize
        # words that appears first in the text.
        relevant_words = collections.OrderedDict()
        for w in words:
            if w and w not in stop_words:
                relevant_words[w] = relevant_words.get(w, 0) + 1

        relevant_words = [(w, c) for w,c in six.iteritems(relevant_words)]
        relevant_words.sort(key=operator.itemgetter(1), reverse=True)
        return ', '.join(w for w, c in relevant_words[:max_words])

    def get_meta_title(self, max_length=100, end_text='...'):
        if self.meta_title:
            title = self.meta_title
        else:
            title = ''
            field_names = {fld.name for fld in self._meta.get_fields()}
            for field_name in ('title', 'headline', 'name'):
                if field_name in field_names:
                    title = getattr(self, field_name)
                    if title:
                        break

        title = strip_tags(title)
        title = Truncator(title).chars(max_length, end_text)
        return title

