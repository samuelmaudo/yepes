# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from django.db import models
from django.utils.translation import ugettext_lazy as _

from yepes.apps.standards.managers import (
    CountryManager,
    CountrySubdivisionManager,
    CurrencyManager,
    LanguageManager,
    RegionManager,
)
from yepes.apps.standards.model_mixins import Standard
from yepes.model_mixins import Enableable, Nestable, ParentForeignKey


class AbstractCountry(Enableable, Standard):

    region = models.ForeignKey(
            'Region',
            related_name='countries',
            verbose_name=_('Region'))
    code = models.CharField(
            unique=True,
            max_length=2,
            verbose_name=_('Code'),
            help_text=_('Specify 2-letter country code, for example "ES".'))
    long_code = models.CharField(
            unique=True,
            max_length=3,
            verbose_name=_('Long Code'),
            help_text=_('Specify 3-letter country code, for example "ESP".'))
    number = models.CharField(
            unique=True,
            max_length=3,
            verbose_name=_('Number'),
            help_text=_('Specify numeric country code, for example "724".'))

    objects = CountryManager()

    class Meta:
        abstract = True
        ordering = ['name']
        verbose_name = _('Country')
        verbose_name_plural = _('Countries')

    @staticmethod
    def autocomplete_search_fields():
        return ('name__icontains',
                'code__iexact',
                'long_code__iexact',
                'number__iexact')

    def natural_key(self):
        return (self.code, )

AbstractCountry._meta.get_field('name', False).help_text = _(
    'You can find country names and ISO codes here: '
    '<a target="_blank" href="http://en.wikipedia.org/wiki/ISO_3166-1">'
    'http://en.wikipedia.org/wiki/ISO_3166-1'
    '</a>'
)


class AbstractCountrySubdivision(Enableable, Standard):

    country = models.ForeignKey(
            'Country',
            related_name='subdivisions',
            verbose_name=_('Country'))
    code = models.CharField(
            unique=True,
            max_length=6,
            verbose_name=_('Code'),
            help_text=_('Specify country subdivision code, for example "ES-O".'))

    objects = CountrySubdivisionManager()

    class Meta:
        abstract = True
        ordering = ['name']
        verbose_name = _('Country Subdivision')
        verbose_name_plural = _('Country Subdivisions')

    @staticmethod
    def autocomplete_search_fields():
        return ('name__icontains',
                'code__iexact')

    def natural_key(self):
        return (self.code, )


class AbstractCurrency(Enableable, Standard):

    symbol = models.CharField(
            db_index=True,
            max_length=7,
            verbose_name=_('Symbol'),
            help_text=_('Specify currency symbol, for example "€".'))
    code = models.CharField(
            unique=True,
            max_length=3,
            verbose_name=_('Code'),
            help_text=_('Specify 3-letter currency code, for example "EUR".'))
    number = models.CharField(
            unique=True,
            max_length=3,
            verbose_name=_('Number'),
            help_text=_('Specify numeric currency code, for example "978".'))

    # Additional info
    decimals = models.PositiveSmallIntegerField(
            default=2,
            blank=True,
            verbose_name=_('Decimals'),
            help_text=_('Number of digits after the decimal separator.'))
    countries = models.ManyToManyField(
            'Country',
            blank=True,
            related_name='currencies',
            verbose_name=_('Countries'),
            help_text=_('Countries using this currency.'))

    objects = CurrencyManager()

    class Meta:
        abstract = True
        ordering = ['name']
        verbose_name = _('Currency')
        verbose_name_plural = _('Currencies')

    @staticmethod
    def autocomplete_search_fields():
        return ('name__icontains',
                'code__iexact',
                'number__iexact')

    def natural_key(self):
        return (self.code, )

AbstractCurrency._meta.get_field('name', False).help_text = _(
    'You can find currency names and ISO codes here: '
    '<a target="_blank" href="http://en.wikipedia.org/wiki/ISO_4217">'
    'http://en.wikipedia.org/wiki/ISO_4217'
    '</a>'
)


class AbstractLanguage(Enableable, Standard):

    tag = models.CharField(
            unique=True,
            max_length=3,
            verbose_name=_('Tag'),
            help_text=_('You can find an explanation about the language tags here: '
                        '<a target="_blank" href="http://www.w3.org/International/articles/language-tags/Overview.en.php">'
                        'http://www.w3.org/International/articles/language-tags/Overview.en.php'
                        '</a>'))
    iso_639_1 = models.CharField(
            blank=True,
            db_index=True,
            max_length=2,
            verbose_name=_('ISO 639-1'),
            help_text=_('Specify 2-letter language code, for example "es".'))
    iso_639_2 = models.CharField(
            blank=True,
            db_index=True,
            max_length=3,
            verbose_name=_('ISO 639-2'),
            help_text=_('Specify 3-letter language code, for example "spa".'))
    iso_639_3 = models.CharField(
            blank=True,
            db_index=True,
            max_length=3,
            verbose_name=_('ISO 639-3'),
            help_text=_('Specify 3-letter language code, for example "spa".'))

    # Additional info
    countries = models.ManyToManyField(
            'Country',
            blank=True,
            related_name='languages',
            verbose_name=_('Countries'),
            help_text=_('Countries where this language is official.'))

    objects = LanguageManager()

    class Meta:
        abstract = True
        ordering = ['name']
        verbose_name = _('Language')
        verbose_name_plural = _('Languages')

    @staticmethod
    def autocomplete_search_fields():
        return ('name__icontains',
                'tag__iexact',
                'iso_639_1__iexact',
                'iso_639_2__iexact',
                'iso_639_3__iexact')

    def natural_key(self):
        return (self.tag, )

    @property
    def code(self):
        return self.tag

AbstractLanguage._meta.get_field('name', False).help_text = _(
    'You can find language names and ISO codes here: '
    '<a target="_blank" href="http://en.wikipedia.org/wiki/List_of_ISO_639-3_codes">'
    'http://en.wikipedia.org/wiki/List_of_ISO_639-3_codes'
    '</a>'
)


class AbstractRegion(Nestable, Standard):

    parent = ParentForeignKey(
            'self',
            null=True,
            related_name='children',
            verbose_name=_('Parent Region'))
    number = models.CharField(
            unique=True,
            max_length=3,
            verbose_name=_('Number'),
            help_text=_('Specify numeric region code, for example "150".'))

    objects = RegionManager()

    class Meta:
        abstract = True
        ordering = ['name']
        verbose_name = _('Region')
        verbose_name_plural = _('Regions')

    @staticmethod
    def autocomplete_search_fields():
        return ('name__icontains',
                'number__iexact')

    def natural_key(self):
        return (self.number, )

    @property
    def code(self):
        return self.number


AbstractRegion._meta.get_field('name', False).verbose_name = _('Name')
AbstractRegion._meta.get_field('name', False).help_text = _(
    'You can find region names and United Nations codes here: '
    '<a target="_blank" href="http://en.wikipedia.org/wiki/UN_M.49">'
    'http://en.wikipedia.org/wiki/UN_M.49'
    '</a>'
)

