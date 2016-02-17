# -*- coding:utf-8 -*-

from __future__ import unicode_literals

import re

from django.contrib.sites.models import Site
from django.http import HttpResponseNotFound

from yepes.contrib.registry import registry


class SubdomainsMiddleware(object):
    """
    Middleware that adds a ``subdomain`` attribute to the request object,
    which corresponds to the portion of the URL before the ``domain``
    attribute of the current ``Site``.

    If the subdomain is not one of the ``ALLOWED_SUBDOMAINS``, returns a
    NOT FOUND response.

    """
    def process_request(self, request):
        site = Site.objects.get_current()
        domain = site.domain
        pattern = r'^(?:(?P<subdomain>.*?)\.)?{0}(?P<addons>.*)$'
        match = re.match(pattern.format(re.escape(domain)),
                         request.get_host())
        if match:
            subdomain = match.group('subdomain') or ''
            addons = match.group('addons') or ''
        else:
            subdomain = ''
            addons = ''

        allowed_subdomains = registry.get('core:ALLOWED_SUBDOMAINS', ())
        if allowed_subdomains and subdomain not in allowed_subdomains:
            return HttpResponseNotFound()

        request.subdomain = subdomain

