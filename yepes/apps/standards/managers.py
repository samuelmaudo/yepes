# -*- coding:utf-8 -*-

from django.db.models import F, Q

from yepes.cache import LookupTable
from yepes.loading import get_class
from yepes.managers import (
    EnableableManager, EnableableQuerySet,
    NestableManager,
)

GeographicAreaProxy = get_class('standards.proxies', 'GeographicAreaProxy')


class CountryManager(EnableableManager):

    def get_by_natural_key(self, code):
        if code.isdigit():
            return self.get(number=code)
        elif len(code) == 2:
            return self.get(code=code)
        elif len(code) == 3:
            return self.get(code_long=code)
        else:
            raise self.model.DoesNotExists


class CountrySubdivisionQuerySet(EnableableQuerySet):

    def disabled(self):
        """
        Returns disabled country subdivisions.
        """
        return self.filter(Q(country__is_enabled=False) | Q(is_enabled=False))

    def enabled(self):
        """
        Returns enabled country subdivisions.
        """
        return self.filter(Q(country__is_enabled=True) & Q(is_enabled=True))


class CountrySubdivisionManager(EnableableManager):

    def get_queryset(self):
        return CountrySubdivisionQuerySet(self.model, using=self._db)

    def get_by_natural_key(self, code):
        return self.get(code=code)


class CurrencyManager(EnableableManager):

    def get_by_natural_key(self, code):
        if code.isdigit():
            return self.get(number=code)
        else:
            return self.get(code=code)


class GeographicAreaLookupTable(LookupTable):

    def fetch_records(self):
        qs = super(GeographicAreaLookupTable, self).fetch_records()
        return [GeographicAreaProxy(area) for area in qs]


class LanguageManager(EnableableManager):

    def get_by_natural_key(self, tag):
        return self.get(tag=tag)


class RegionManager(NestableManager):

    def get_by_natural_key(self, number):
        return self.get(number=number)

