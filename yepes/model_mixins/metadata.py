# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from collections import Counter
import re

from django.db import models
from django.utils.html import strip_tags
from django.utils.text import Truncator
from django.utils.translation import ugettext_lazy as _

from yepes import fields
from yepes.apps.registry import registry

__all__ = ('MetaData', )

WORD_SEPARATORS_RE = re.compile(r'[\s\(\)\[\]\{\}\\\/\-+*%<>=.,:;&|#@¿?¡!]+')


class MetaData(models.Model):
    """
    Abstract model that provides meta data for content.
    """

    meta_title = models.CharField(
            blank=True,
            max_length=127,
            verbose_name=_('Title'),
            help_text=_('Optional title to be used in the HTML title tag. '
                        'If left blank, the main title field will be used.'))
    meta_description = models.TextField(
            blank=True,
            verbose_name=_('Description'),
            help_text=_('Optional description to be used in the description meta tag. '
                        'If left blank, the content field will be used.'))
    meta_keywords = fields.CommaSeparatedField(
            blank=True,
            verbose_name=_('Keywords'),
            help_text=_('Optional keywords to be used in the keywords meta tag. '
                        'If left blank, will be extracted from the description.'))

    class Meta:
        abstract = True

    def get_meta_description(self, max_words=30, end_text='...'):
        if self.meta_description:
            return self.meta_description

        description = ''
        field_names = self._meta.get_all_field_names()
        if 'description' in field_names:
            description = self.description
        if not description and 'excerpt' in field_names:
            description = self.excerpt
        if not description and 'content' in field_names:
            description = self.content
        if not description:
            for field in self._meta.fields:
                if isinstance(field, models.TextField):
                    description = getattr(self, field.name)
                    if description:
                        break

        description = strip_tags(description)
        description = Truncator(description).words(max_words, end_text)
        return description

    def get_meta_keywords(self, max_words=10):
        if self.meta_keywords:
            return ', '.join(self.meta_keywords)

        words = []
        words.extend(WORD_SEPARATORS_RE.split(self.get_meta_title().lower()) * 2)
        words.extend(WORD_SEPARATORS_RE.split(self.get_meta_description().lower()))

        stop_words = registry['core:STOP_WORDS']
        relevant_words = Counter(w for w in words if w and w not in stop_words)
        return ', '.join(w for w, c in relevant_words.most_common(max_words))

    def get_meta_title(self, max_length=100, end_text='...'):
        if self.meta_title:
            return self.meta_title

        title = ''
        field_names = self._meta.get_all_field_names()
        if 'title' in field_names:
            title = self.title
        if not title and 'name' in field_names:
            title = self.name

        title = strip_tags(title)
        if len(title) > max_length:
            title = title[:max_length] + end_text

        return title
