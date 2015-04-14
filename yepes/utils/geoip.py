# -*- coding:utf-8 -*-

from __future__ import unicode_literals

try:

    import geoip2.database
    import geoip2.errors

except ImportError:


    import os

    import GeoIP as MaxMindApi

    from django.core.validators import ipv4_re as IPV4_RE
    from django.utils import six
    from django.utils.ipv6 import is_valid_ipv6_address

    from yepes.conf import settings
    from yepes.types import Undefined

    __all__ = ('GeoIP', )


    def is_valid_ipv4_address(ip_str):
        return (IPV4_RE.search(ip_str) is not None)


    class GeoIP(object):

        _asnum_database = Undefined
        _asnum_v6_database = Undefined
        _city_database = Undefined
        _city_v6_database = Undefined
        _country_database = Undefined
        _country_v6_database = Undefined

        def __init__(self, path=None, cache=None,
                        country=None, country_v6=None,
                        city=None, city_v6=None,
                        asnum=None, asnum_v6=None):
            if path is None:
                path = settings.GEOIP_PATH
            if cache is None:
                cache = getattr(settings, 'GEOIP_USE_CACHE', False)
            if country is None:
                country = getattr(settings, 'GEOIP_COUNTRY', 'GeoIP.dat')
            if country_v6 is None:
                country_v6 = getattr(settings, 'GEOIP_COUNTRY_V6', 'GeoIPv6.dat')
            if city is None:
                city = getattr(settings, 'GEOIP_CITY', 'GeoLiteCity.dat')
            if city_v6 is None:
                city_v6 = getattr(settings, 'GEOIP_CITY_V6', 'GeoLiteCityv6.dat')
            if asnum is None:
                asnum = getattr(settings, 'GEOIP_ASNUM', 'GeoIPASNum.dat')
            if asnum_v6 is None:
                asnum_v6 = getattr(settings, 'GEOIP_ASNUM_V6', 'GeoIPASNumv6.dat')

            self._country_path = os.path.join(path, country)
            self._country_v6_path = os.path.join(path, country_v6)
            self._city_path = os.path.join(path, city)
            self._city_v6_path = os.path.join(path, city_v6)
            self._asnum_path = os.path.join(path, asnum)
            self._asnum_v6_path = os.path.join(path, asnum_v6)
            if cache:
                self._mode = MaxMindApi.GEOIP_MEMORY_CACHE
            else:
                self._mode = MaxMindApi.GEOIP_STANDARD

        @property
        def _asnum(self):
            if self._asnum_database is Undefined:
                self._asnum_database = MaxMindApi.open(self._asnum_path,
                                                    self._mode)
            return self._asnum_database

        @property
        def _asnum_v6(self):
            if self._asnum_v6_database is Undefined:
                self._asnum_v6_database = MaxMindApi.open(self._asnum_v6_path,
                                                        self._mode)
            return self._asnum_v6_database

        @property
        def _city(self):
            if self._city_database is Undefined:
                self._city_database = MaxMindApi.open(self._city_path,
                                                    self._mode)
            return self._city_database

        @property
        def _city_v6(self):
            if self._city_v6_database is Undefined:
                self._city_v6_database = MaxMindApi.open(self._city_v6_path,
                                                        self._mode)
            return self._city_v6_database

        @property
        def _country(self):
            if self._country_database is Undefined:
                self._country_database = MaxMindApi.open(self._country_path,
                                                        self._mode)
            return self._country_database

        @property
        def _country_v6(self):
            if self._country_v6_database is Undefined:
                self._country_v6_database = MaxMindApi.open(self._country_v6_path,
                                                            self._mode)
            return self._country_v6_database

        def city(self, query):
            """
            Returns a dictionary of city information for the given IP address or
            Fully Qualified Domain Name (FQDN). Some information in the dictionary
            may be undefined (None).
            """
            information = {
                'continent_code': None,
                'country_code': None,
                'country_code3': None,
                'country_name': None,
                'region': None,
                'region_name': None,
                'city': None,
                'time_zone': None,
                'area_code': 0,
                'dma_code': 0,
                'postal_code': None,
                'latitude': 0.0,
                'longitude': 0.0,
            }
            if is_valid_ipv4_address(query):
                record = self._city.record_by_addr(query)
            elif is_valid_ipv6_address(query):
                record = self._city_v6.record_by_addr_v6(query)
            else:
                record = self._city.record_by_name(query)

            if record is not None:
                for key, value in six.iteritems(record):
                    if isinstance(value, six.binary_type):
                        value = value.decode('latin_1', 'replace')
                    information[key] = value

            return information

        def country(self, query):
            """
            Returns a dictonary with with the country code and name when given an
            IP address or a Fully Qualified Domain Name (FQDN).

            For example, both '24.124.1.80' and 'djangoproject.com' are valid
            parameters.

            """
            name = None
            if is_valid_ipv4_address(query):
                code = self._country.country_code_by_addr(query)
                if code is not None:
                    name = self._country.country_name_by_addr(query)
            elif is_valid_ipv6_address(query):
                code = self._country_v6.country_code_by_addr_v6(query)
                if code is not None:
                    name = self._country_v6.country_name_by_addr_v6(query)
            else:
                code = self._country.country_code_by_name(query)
                if code is not None:
                    name = self._country.country_name_by_name(query)

            if isinstance(code, six.binary_type):
                code = code.decode('latin_1', 'replace')

            if isinstance(name, six.binary_type):
                name = name.decode('latin_1', 'replace')

            return {
                'country_code': code,
                'country_name': name,
            }

        def country_code(self, query):
            """
            Returns the country code for the given IP Address or FQDN.
            """
            return self.country(query).get('country_code')

        def country_name(self, query):
            """
            Returns the country name for the given IP Address or FQDN.
            """
            return self.country(query).get('country_name')

        def provider(self, query):
            """
            Returns a tuple with the number and the name of the Internet service
            provider for the given IP Address or FQDN.
            """
            information = {
                'provider_number': None,
                'provider_name': None,
            }
            if is_valid_ipv4_address(query):
                provider = self._asnum.org_by_addr(query)
            elif is_valid_ipv6_address(query):
                #provider = self._asnum_v6.org_by_addr_v6(query)
                provider = None
            else:
                provider = self._asnum.org_by_name(query)

            if provider is not None:
                provider = provider.decode('latin_1', 'replace')
                provider = provider.split(' ', 1)
                number = provider[0]
                name = provider[1] if len(provider) > 1 else ''
                information['provider_number'] = number
                information['provider_name'] = name

            return information

        def provider_name(self, query):
            """
            Returns the name of the Internet service provider for the given IP
            Address or FQDN.
            """
            return self.provider(query).get('provider_name')

        def provider_number(self, query):
            """
            Returns the number of the Internet service provider for the given IP
            Address or FQDN.
            """
            return self.provider(query).get('provider_number')


    geoip = GeoIP()


else:


    import os

    from yepes.conf import settings
    from yepes.utils.properties import cached_property

    __all__ = ('GeoIP2', )


    class GeoIP2(object):

        def __init__(self, path=None, locales=None, country=None, city=None):
            if path is None:
                path = settings.GEOIP_PATH
            if locales is None:
                locales = getattr(settings, 'GEOIP_LOCALES', None)
            if country is None:
                country = getattr(settings, 'GEOIP_COUNTRY', 'GeoLite2-Country.mmdb')
            if city is None:
                city = getattr(settings, 'GEOIP_CITY', 'GeoLite2-City.mmdb')

            self._locales = locales
            self._country_path = os.path.join(path, country)
            self._city_path = os.path.join(path, city)

        @cached_property
        def _city_reader(self):
            return geoip2.database.Reader(self._city_path)

        @cached_property
        def _country_reader(self):
            return geoip2.database.Reader(self._country_path)

        def city(self, ip_address):
            """
            Returns a dictionary of city information for the given IP address. Some
            information in the dictionary may be undefined (None).
            """
            try:
                response = self._city_reader.city(ip_address)
            except geoip2.errors.AddressNotFoundError:
                return {
                    'continent_code': None,
                    'country_code': None,
                    'country_code3': None,
                    'country_name': None,
                    'region': None,
                    'region_name': None,
                    'city': None,
                    'time_zone': None,
                    'area_code': 0,
                    'dma_code': 0,
                    'postal_code': None,
                    'latitude': 0.0,
                    'longitude': 0.0,
                }
            else:
                city = response.city
                continent = response.continent
                country = response.country
                location = response.location
                subdivision = response.subdivisions.most_specific
                return {
                    'continent_code': continent.code,
                    'country_code': country.iso_code,
                    'country_code3': None,
                    'country_name': country.name,
                    'region': subdivision.iso_code,
                    'region_name': subdivision.name,
                    'city': city.name,
                    'time_zone': location.time_zone,
                    'area_code': 0,
                    'dma_code': 0,
                    'postal_code': response.postal.code,
                    'latitude': location.latitude,
                    'longitude': location.longitude,
                }

        def country(self, ip_address):
            """
            Returns a dictonary with with the country code and name when given an
            IP address.
            """
            try:
                response = self._country_reader.country(ip_address)
            except geoip2.errors.AddressNotFoundError:
                return {
                    'country_code': None,
                    'country_name': None,
                }
            else:
                country = response.country
                return {
                    'country_code': country.iso_code,
                    'country_name': country.name,
                }

        def country_code(self, ip_address):
            """
            Returns the country code for the given IP Address.
            """
            return self.country(ip_address).get('country_code')

        def country_name(self, ip_address):
            """
            Returns the country name for the given IP Address.
            """
            return self.country(ip_address).get('country_name')


    geoip = GeoIP2()

