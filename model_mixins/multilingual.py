# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import re

from django.db import models
import django.db.models.options as options
from django.core.exceptions import ObjectDoesNotExist
from django.utils.encoding import force_text
from django.utils.translation import get_language

from yepes.conf import settings
from yepes.exceptions import MissingAttributeError
from yepes.loading import get_model

__all__ = ('InvalidLanguageTag', 'Multilingual', 'TranslationDoesNotExist')

options.DEFAULT_NAMES += ('translation', 'multilingual')

LANGUAGE_TAG_RE = re.compile(r'^(?P<lang>[a-z]{2,3})(?P<extra>[-a-zA-Z]*)$')
TRANSLATED_ATTRIBUTE_RE = re.compile(r'^(?P<attr>\w+?)_(?P<tag>[a-z_]{2,5})$')


class InvalidLanguageTag(ValueError):

    def __init__(self, model, tag):
        msg = "'{0}' is not a valid language tag."
        super(TranslationDoesNotExist, self).__init__(msg.format(tag))
        self.language_tag = tag


class TranslationDoesNotExist(ValueError):

    def __init__(self, model, tag):
        msg = "'{0}' has no translation for '{1}' language"
        super(TranslationDoesNotExist, self).__init__(msg.format(model, tag))
        self.model = model
        self.language_tag = tag


class Multilingual(models.Model):
    """
    Provides support for multilingual fields.

    Example:

    class Language(models.Model):
        tag = models.CharField(max_length=5)
        name = models.CharField(max_length=16)

    class BookTranslation(models.Model):
        language = models.ForeignKey("Language")
        title = models.CharField(max_length=32)
        description = models.TextField()
        model = models.ForeignKey("Book")

    class Book(Multilingual):
        ISBN = models.IntegerField()

        class Meta:
            translation = 'BookTranslation'
            multilingual = ['title', 'description']

    lang_en = Language(tag="en", name="English")
    lang_en.save()
    lang_pl = Language(tag="pl", name="Polish")
    lang_pl.save()
    book = Book(ISBN="1234567890")
    book.save()
    book_en = BookTranslation()
    book_en.title = "Django for Dummies"
    book_en.description = "Django described in simple words."
    book_en.model = book
    book_en.save()
    book_pl = BookTranslation()
    book_pl.title = "Django dla Idiotow"
    book_pl.description = "Django opisane w prostych slowach"
    book_pl.model = book
    book_pl.save()

    # now here comes the magic
    book.title_en
    'Django for Dummies'
    book.description_pl
    'Django opisane w prostych slowach'

    """
    class Meta:
        abstract = True

    def __init__(self, *args, **kwargs):
        super(Multilingual, self).__init__(*args, **kwargs)
        self._language = get_language()[:2]
        self._translations = dict()

    def __getattr__(self, attr):
        if attr in self._meta.multilingual:
            tag = self._language
            field = attr
        else:
            match = TRANSLATED_ATTRIBUTE_RE.search(attr)
            if (match is None
                    or match.groups('attr') not in self._meta.multilingual):
                raise MissingAttributeError(self, attr)

            tag = match.groups('tag')

        translation = self.get_translation(tag)
        if translation is None:
            return None
        else:
            return getattr(translation, field)

    def clean_language_tag(self, tag):
        tag = force_text(tag).replace('_', '-')
        match = LANGUAGE_TAG_RE.search(tag)
        if not match:
            raise InvalidLanguageTag(tag)
        else:
            return match.group('lang')

    def for_language(self, tag):
        """
        Sets the language for the translation fields of this object.
        """
        self._language = self.clean_language_tag(tag)

    def get_translation(self, tag):
        """
        Returns the translation object for given language ``tag``.
        """
        tag = self.clean_language_tag(tag)
        if tag not in self._translations:
            Translation = get_model(self._meta.app_label,
                                    self._meta.translation)
            translation = None
            qs = Translation._default_manager.select_related()
            try:
                translation = qs.get(model=self, language__tag=tag)
            except ObjectDoesNotExist:
                if (settings.MULTILINGUAL_FALL_BACK_TO_DEFAULT
                        and settings.MULTILINGUAL_DEFAULT
                        and tag != settings.MULTILINGUAL_DEFAULT):
                    return self.get_translation(settings.MULTILINGUAL_DEFAULT)
                elif (settings.DEBUG
                        or not settings.MULTILINGUAL_FAIL_SILENTLY):
                    raise TranslationDoesNotExist(self, tag)

            self._translations[tag] = translation

        return self._translations[tag]

    def refresh_translations(self):
        self._translations.clear()

