# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from django.db import models
from django.utils.translation import ugettext_lazy as _

from yepes import fields


class CountryField(models.ForeignKey):

    description = _('Many-to-one relationship with Country model.')

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('to', 'standards.Country')
        kwargs.setdefault('limit_choices_to', {'is_enabled': True})
        kwargs.setdefault('on_delete', models.PROTECT)
        kwargs.setdefault('related_name', '%(app_label)s_%(class)s_related+')
        kwargs.setdefault('verbose_name', _('Country'))
        super(CountryField, self).__init__(*args, **kwargs)


class CountriesField(models.ManyToManyField):

    description = _('Many-to-many relationship with Country model.')

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('to', 'standards.Country')
        kwargs.setdefault('limit_choices_to', {'is_enabled': True})
        kwargs.setdefault('related_name', '%(app_label)s_%(class)s_related+')
        kwargs.setdefault('verbose_name', _('Countries'))
        super(CountriesField, self).__init__(*args, **kwargs)


class CountrySubdivisionField(models.ForeignKey):

    description = _('Many-to-one relationship with CountrySubdivision model.')

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('to', 'standards.CountrySubdivision')
        kwargs.setdefault('limit_choices_to', {'country__is_enabled': True, 'is_enabled': True})
        kwargs.setdefault('on_delete', models.PROTECT)
        kwargs.setdefault('related_name', '%(app_label)s_%(class)s_related+')
        kwargs.setdefault('verbose_name', _('Subdivision'))
        super(CountrySubdivisionField, self).__init__(*args, **kwargs)


class CountrySubdivisionsField(models.ManyToManyField):

    description = _('Many-to-many relationship with CountrySubdivision model.')

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('to', 'standards.CountrySubdivision')
        kwargs.setdefault('limit_choices_to', {'country__is_enabled': True,
                                               'is_enabled': True})
        kwargs.setdefault('related_name', '%(app_label)s_%(class)s_related+')
        kwargs.setdefault('verbose_name', _('Subdivisions'))
        super(CountrySubdivisionsField, self).__init__(*args, **kwargs)


class CurrencyField(models.ForeignKey):

    description = _('Many-to-one relationship with Currency model.')

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('to', 'standards.Currency')
        kwargs.setdefault('limit_choices_to', {'is_enabled': True})
        kwargs.setdefault('on_delete', models.PROTECT)
        kwargs.setdefault('related_name', '%(app_label)s_%(class)s_related+')
        kwargs.setdefault('verbose_name', _('Currency'))
        super(CurrencyField, self).__init__(*args, **kwargs)


class CurrenciesField(models.ManyToManyField):

    description = _('Many-to-many relationship with Currency model.')

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('to', 'standards.Currency')
        kwargs.setdefault('limit_choices_to', {'is_enabled': True})
        kwargs.setdefault('related_name', '%(app_label)s_%(class)s_related+')
        kwargs.setdefault('verbose_name', _('Currencies'))
        super(CurrenciesField, self).__init__(*args, **kwargs)


class GeographicAreaField(fields.CachedForeignKey):

    description = _('Many-to-one relationship with GeographicArea model.')

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('to', 'standards.GeographicArea')
        kwargs.setdefault('on_delete', models.PROTECT)
        kwargs.setdefault('related_name', '%(app_label)s_%(class)s_related+')
        kwargs.setdefault('verbose_name', _('Geographic Area'))
        super(GeographicAreaField, self).__init__(*args, **kwargs)


class LanguageField(models.ForeignKey):

    description = _('Many-to-one relationship with Language model.')

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('to', 'standards.Language')
        kwargs.setdefault('limit_choices_to', {'is_enabled': True})
        kwargs.setdefault('on_delete', models.PROTECT)
        kwargs.setdefault('related_name', '%(app_label)s_%(class)s_related+')
        kwargs.setdefault('verbose_name', _('Language'))
        super(LanguageField, self).__init__(*args, **kwargs)


class LanguagesField(models.ManyToManyField):

    description = _('Many-to-many relationship with Language model.')

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('to', 'standards.Language')
        kwargs.setdefault('limit_choices_to', {'is_enabled': True})
        kwargs.setdefault('related_name', '%(app_label)s_%(class)s_related+')
        kwargs.setdefault('verbose_name', _('Languages'))
        super(LanguagesField, self).__init__(*args, **kwargs)


class RegionField(models.ForeignKey):

    description = _('Many-to-one relationship with Region model.')

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('to', 'standards.Region')
        kwargs.setdefault('on_delete', models.PROTECT)
        kwargs.setdefault('related_name', '%(app_label)s_%(class)s_related+')
        kwargs.setdefault('verbose_name', _('Region'))
        super(RegionField, self).__init__(*args, **kwargs)


class RegionsField(models.ManyToManyField):

    description = _('Many-to-many relationship with Region model.')

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('to', 'standards.Region')
        kwargs.setdefault('on_delete', models.PROTECT)
        kwargs.setdefault('related_name', '%(app_label)s_%(class)s_related+')
        kwargs.setdefault('verbose_name', _('Regions'))
        super(RegionsField, self).__init__(*args, **kwargs)

