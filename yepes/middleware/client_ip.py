# -*- coding:utf-8 -*-

from __future__ import unicode_literals

import re

from django.core.exceptions import ValidationError
from django.core.validators import ipv4_re as IPV4_RE
from django.http import HttpResponseForbidden
from django.utils.ipv6 import clean_ipv6_address

from yepes.contrib.registry import registry
from yepes.utils.http import get_meta_data

COMMA_RE = re.compile(r'\s*,\s*')


class ClientIpMiddleware(object):
    """
    Middleware that adds a ``client_ip`` attribute to the request object, with
    the  IP address of the client.

    Moreover, if this address is one of the ``BANNED_IP_ADDRESSES``, returns a
    FORBIDDEN response.

    """
    def process_request(self, request):
        banned_addresses = registry.get('core:BANNED_IP_ADDRESSES', ())
        client_addresses = COMMA_RE.split('{0},{1},{2}'.format(
            get_meta_data(request, 'HTTP_X_FORWARDED_FOR'),
            get_meta_data(request, 'HTTP_X_REAL_IP'),
            get_meta_data(request, 'REMOTE_ADDR'),
        ))
        for address in client_addresses:
            if not address:
                continue

            if ':' in address:
                try:
                    address = clean_ipv6_address(address)
                except ValidationError:
                    continue
            elif not IPV4_RE.search(address):
                continue

            if address in banned_addresses:
                return HttpResponseForbidden()
            else:
                request.client_ip = address
                break
        else:
            request.client_ip = '127.0.0.1'

