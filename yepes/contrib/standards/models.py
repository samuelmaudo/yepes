# -*- coding:utf-8 -*-

from yepes.apps import apps

AbstractCountry = apps.get_class('standards.abstract_models', 'AbstractCountry')
AbstractCountrySubdivision = apps.get_class('standards.abstract_models', 'AbstractCountrySubdivision')
AbstractCurrency = apps.get_class('standards.abstract_models', 'AbstractCurrency')
AbstractGeographicArea = apps.get_class('standards.abstract_models', 'AbstractGeographicArea')
AbstractLanguage = apps.get_class('standards.abstract_models', 'AbstractLanguage')
AbstractRegion = apps.get_class('standards.abstract_models', 'AbstractRegion')


class Country(AbstractCountry):
    pass

class CountrySubdivision(AbstractCountrySubdivision):
    pass

class Currency(AbstractCurrency):
    pass

class GeographicArea(AbstractGeographicArea):
    pass

class Language(AbstractLanguage):
    pass

class Region(AbstractRegion):
    pass

