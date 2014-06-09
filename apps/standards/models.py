# -*- coding:utf-8 -*-

from yepes.apps.standards.abstract_models import (
    AbstractCountry,
    AbstractCountrySubdivision,
    AbstractCurrency,
    AbstractGeographicArea,
    AbstractLanguage,
    AbstractRegion,
)

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
