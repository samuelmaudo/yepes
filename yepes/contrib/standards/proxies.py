# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from django.db.models.base import ModelState
from django.utils import six
from django.utils import translation
from django.utils.encoding import force_str, python_2_unicode_compatible

from yepes.conf import settings
from yepes.contrib.standards.model_mixins import NAME_RE
from yepes.exceptions import MissingAttributeError
from yepes.loading import get_model
from yepes.utils.properties import cached_property


@python_2_unicode_compatible
class GeographicAreaProxy(object):

    def __init__(self, area):
        self._state = ModelState()
        self.id = self.pk = area.pk
        self.api_id = area.api_id
        self.name = area.name
        for attr_name, attr_value in six.iteritems(area.__dict__):
            if attr_name.startswith('_name_'):
                setattr(self, attr_name, attr_value)

        self.included_countries = frozenset(
            country.pk
            for country
            in area.included_countries.all()
        )
        self.included_country_codes = frozenset(
            country.code
            for country
            in area.included_countries.all()
        )
        self.excluded_countries = frozenset(
            country.pk
            for country
            in area.excluded_countries.all()
        )
        self.excluded_country_codes = frozenset(
            country.code
            for country
            in area.excluded_countries.all()
        )
        self.included_subdivisions = frozenset(
            subdivision.pk
            for subdivision
            in area.included_subdivisions.all()
        )
        self.included_subdivision_codes = frozenset(
            subdivision.code
            for subdivision
            in area.included_subdivisions.all()
        )
        self.excluded_subdivisions = frozenset(
            subdivision.pk
            for subdivision
            in area.excluded_subdivisions.all()
        )
        self.excluded_subdivision_codes = frozenset(
            subdivision.code
            for subdivision
            in area.excluded_subdivisions.all()
        )

    def __getattr__(self, attr_name):
        if NAME_RE.search(attr_name) is None:
            raise MissingAttributeError(self, attr_name)

        name = self.__dict__.get(''.join(('_', attr_name)))
        if name:
            return name

        fallback = settings.STANDARDS_FALLBACK_TRANSLATION
        if fallback != 'native':
            name = self.__dict__.get(''.join(('_name_', fallback)))
            if name:
                return name

        return self.name

    def __repr__(self):
        args = (
            self.__class__.__name__,
            self,
        )
        return force_str("<{0}: '{1}'>".format(*args))

    def __setattr__(self, attr_name, attr_value):
        if attr_name.startswith('_') or NAME_RE.search(attr_name) is None:
            super(GeographicAreaProxy, self).__setattr__(attr_name, attr_value)
        else:
            self.__dict__[''.join(('_', attr_name))] = attr_value

    def __str__(self):
        if settings.STANDARDS_DEFAULT_TRANSLATION == 'native':
            return self.name

        if settings.STANDARDS_DEFAULT_TRANSLATION == 'locale':
            language = translation.get_language()
        else:
            language = settings.STANDARDS_DEFAULT_TRANSLATION

        return getattr(self, ''.join(('name_', language[:2])))

    def _get_pk_val(self):
        return self.pk

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
        if isinstance(country, six.string_types):
            if country in self.excluded_country_codes:
                return False

            if country in self.included_country_codes:
                return True

            return (not self.included_country_codes)
        else:
            if country.pk in self.excluded_countries:
                return False

            if country.pk in self.included_countries:
                return True

            return not self.included_countries

    def contains_subdivision(self, subdivision):
        """
        Checks whether the given subdivision is located within this area.
        """
        if isinstance(subdivision, six.string_types):
            country = subdivision[:2]

            if country in self.excluded_country_codes:
                return False
            if subdivision in self.excluded_subdivision_codes:
                return False

            if country in self.included_country_codes:
                return True
            if subdivision in self.included_subdivision_codes:
                return True

            return not (self.included_country_codes
                        or self.included_subdivision_codes)
        else:
            if subdivision.country_id in self.excluded_countries:
                return False
            if subdivision.pk in self.excluded_subdivisions:
                return False

            if subdivision.country_id in self.included_countries:
                return True
            if subdivision.pk in self.included_subdivisions:
                return True

            return not (self.included_countries
                        or self.included_subdivisions)

    def includes_all_addresses(self):
        """
        Checks whether this area does not make any filter.
        """
        return not (self.included_countries
                    or self.excluded_countries
                    or self.included_subdivisions
                    or self.excluded_subdivisions)

    def includes_all_countries(self):
        """
        Checks whether this area does not make any filter.
        """
        return not (self.included_countries
                    or self.excluded_countries
                    or self.included_subdivisions
                    or self.excluded_subdivisions)

    def includes_all_subdivisions(self):
        """
        Checks whether this area does not make any filter.
        """
        return not (self.included_countries
                    or self.excluded_countries
                    or self.included_subdivisions
                    or self.excluded_subdivisions)

    # Need to pretend to be the wrapped class, for the sake of objects that
    # care about this (especially in equality tests).
    @cached_property
    def __class__(self):
        return get_model('standards', 'GeographicArea')

