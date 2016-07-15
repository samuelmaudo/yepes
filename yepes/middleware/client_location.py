# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from django import VERSION as DJANGO_VERSION
if DJANGO_VERSION < (1, 10):
    MiddlewareMixin = object
else:
    from django.utils.deprecation import MiddlewareMixin

from yepes.utils.geoip import geoip


class ClientLocationMiddleware(MiddlewareMixin):
    """
    Middleware that adds a ``client_location`` attribute to the request object,
    that is a dictionary containing geographic information about the client.

    Requires that MaxMind's Python GeoIP API is installed.

    """
    def process_request(self, request):
        information = geoip.city(request.client_ip)
        if not information.get('country_code'):
            information.update(geoip.country(request.client_ip))

        request.client_location = information

