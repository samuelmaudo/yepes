# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from django.db.models.base import ModelState
from django.utils.encoding import force_str, python_2_unicode_compatible
from django.utils.functional import cached_property

from yepes.conf import settings
from yepes.loading import get_model
from yepes.apps.standards.model_mixins import NAME_RE


@python_2_unicode_compatible
class GeographicAreaProxy(object):

    def __init__(self, area):
        self._state = ModelState()
        self.id = self.pk = area.pk
        self.api_id = area.api_id
        self.name = area.name
        for attr in area.__dict__:
            if NAME_RE.search(attr) is not None:
                getattr(self, attr, area.__dict__[attr])

        self.included_countries = frozenset(
            country.pk
            for country
            in area.included_countries.all()
        )
        self.excluded_countries = frozenset(
            country.pk
            for country
            in area.excluded_countries.all()
        )
        self.included_subdivisions = frozenset(
            subdivision.pk
            for subdivision
            in area.included_subdivisions.all()
        )
        self.excluded_subdivisions = frozenset(
            subdivision.pk
            for subdivision
            in area.excluded_subdivisions.all()
        )

    def __repr__(self):
        args = (
            self.__class__.__name__,
            self,
        )
        return force_str("<{0}: '{1}'>".format(*args))

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

    def contains_address(self, address):
        """
        Checks whether the given address is located within this area.
        """
        if address.country_id in self.excluded_countries:
            return False
        if address.subdivision_id in self.excluded_subdivisions:
            return False

        if address.country_id in self.included_countries:
            return True
        if address.subdivision_id in self.included_subdivisions:
            return True

        if not (self.included_countries
                or self.included_subdivisions):
            return True
        else:
            return False

    def contains_country(self, country):
        """
        Checks whether the given country is located within this area.
        """
        if country.pk in self.excluded_countries:
            return False

        if country.pk in self.included_countries:
            return True

        if not self.included_countries:
            return True
        else:
            return False

    def contains_subdivision(self, subdivision):
        """
        Checks whether the given subdivision is located within this area.
        """
        if subdivision.country_id in self.excluded_countries:
            return False
        if subdivision.pk in self.excluded_subdivisions:
            return False

        if subdivision.country_id in self.included_countries:
            return True
        if subdivision.pk in self.included_subdivisions:
            return True

        if not (self.included_countries
                or self.included_subdivisions):
            return True
        else:
            return False

    def includes_all_addresses(self):
        """
        Checks whether this area does not make any filter.
        """
        return (not self.included_countries
                and not self.excluded_countries
                and not self.included_subdivisions
                and not self.excluded_subdivisions)

    def includes_all_countries(self):
        """
        Checks whether this area does not make any filter.
        """
        return (not self.included_countries
                and not self.excluded_countries)

    def includes_all_subdivisions(self):
        """
        Checks whether this area does not make any filter.
        """
        return (not self.included_countries
                and not self.excluded_countries
                and not self.included_subdivisions
                and not self.excluded_subdivisions)

    # Need to pretend to be the wrapped class, for the sake of objects that
    # care about this (especially in equality tests).
    @cached_property
    def __class__(self):
        return get_model('standards', 'GeographicArea')

