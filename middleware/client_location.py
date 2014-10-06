# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from yepes.utils.geoip import geoip


class ClientLocationMiddleware(object):
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

