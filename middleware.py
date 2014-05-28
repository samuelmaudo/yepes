# -*- coding:utf-8 -*-

from __future__ import unicode_literals

import re

from django.contrib.auth.views import redirect_to_login
from django.contrib.sites.models import Site
from django.core.exceptions import ValidationError
from django.core.validators import ipv4_re as IPV4_RE
from django.http import (
    HttpResponseForbidden,
    HttpResponseNotFound,
    HttpResponsePermanentRedirect,
    HttpResponseRedirect,
)
from django.utils import six, translation
from django.utils.encoding import iri_to_uri
from django.utils.ipv6 import clean_ipv6_address
from django.utils.six.moves.urllib.parse import urlparse

from yepes.apps.registry import registry
from yepes.conf import settings
from yepes.utils.http import get_meta_data
from yepes.utils.phased import second_pass_render

COMMA_RE = re.compile(r'\s*,\s*')


class ClientIpMiddleware(object):

    def process_request(self, request):
        """
        Adds a ``client_ip`` attribute to the request object, with the  IP
        address of the client.

        If this address is one of the ``BANNED_IP_ADDRESSES``, returns an
        ``HttpResponseForbidden`` object.

        """
        request.client_ip = None
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

            if request.client_ip is None:
                request.client_ip = address

        if request.client_ip is None:
            request.client_ip = '127.0.0.1'


class ClientLocationMiddleware(object):

    def process_request(self, request):
        """
        Adds a ``client_location`` attribute to the request object, that is a
        dictionary containing geographic information about the client.

        Requires that MaxMind's Python GeoIP API is installed.

        """
        from yepes.utils.geoip import geoip

        information = geoip.city(request.client_ip)
        information.update(geoip.provider(request.client_ip))

        if not information.get('country_code'):
            information.update(geoip.country(request.client_ip))

        request.client_location = information


class LocaleSubdomainsMiddleware(object):
    """
    Middleware that sets the language based on the request subdomain.
    """

    def process_request(self, request):
        """
        Adds a ``language`` attribute to the request object, which corresponds
        to the ``subdomain``, and activates the translation for this language.
        """
        supported_languages = dict(getattr(settings, 'LANGUAGES', ()))
        language = request.subdomain
        if language not in supported_languages:
            language = getattr(settings, 'LANGUAGE_CODE', 'en')

        translation.activate(language)
        request.language = translation.get_language()

    def process_response(self, request, response):
        """
        Ensures that the ``Content-Language`` is in the response.
        """
        if 'Content-Language' not in response:
            response['Content-Language'] = translation.get_language()

        translation.deactivate()
        return response


class LoginRequiredMiddleware(object):

    def process_request(self, request):
        url = request.get_full_path()
        if (request.user.is_anonymous()
                and urlparse(url).path != settings.LOGIN_URL):
            return redirect_to_login(url)


class PhasedRenderMiddleware(object):
    """
    Performs a second-phase template rendering on the response and should be
    placed before the UpdateCacheMiddleware in the ``MIDDLEWARE_CLASES`` setting.
    """

    def process_response(self, request, response):
        """
        If the content-type starts with ``text/html`` performs a second-phase
        render on response.content and updates the ``Content-Length`` header
        of the response to reflect the change in size after rendering.
        """
        if (not response.streaming
                and response.status_code in (200, 404)
                and response.get('Content-Type', '').startswith('text')):
            response.content = second_pass_render(request, response.content)
            response['Content-Length'] = six.text_type(len(response.content))

        return response


class SSLRedirectMiddleware(object):
    """
    Handles redirections required for SSL when ``SSL_ENABLED`` is ``True``.

    Ensure URLs defined by ``SSL_PATHS`` are redirect to HTTPS, and redirect
    all other URLs to HTTP if on HTTPS.

    This class take code from Mezzanine and Satchmo projects.

    """
    def process_request(self, request):
        if settings.SSL_ENABLED:
            for path in settings.SSL_PATHS:
                if request.path.startswith(path):
                    if not self.request_is_secure(request):
                        return self.redirect(request, secure=True)
                    else:
                        break
            else:
                if self.request_is_secure(request):
                    return self.redirect(request, secure=False)

    # CUSTOM METHODS

    def redirect(self, request, secure, permanent=True):
        if settings.DEBUG and request.method == 'POST':
            msg = "Django can't perform a SSL redirect while maintaining"     \
                  " POST data. Please structure your views so that redirects" \
                  " only occur during GETs."
            raise RuntimeError(msg)

        protocol = 'https' if secure else 'http'
        host = '{0}://{1}'.format(protocol, request.get_host())
        # In certain proxying situations, we need to strip out the 443 port
        # in order to prevent inifinite redirects
        host = host.replace(':443','')

        if settings.SSL_PORT != 443:
            if secure:
                host = '{0}:{1}'.format(host, settings.SSL_PORT)
            else:
                host = host.replace(':{0}'.format(settings.SSL_PORT), '')

        url = '{0}{1}'.format(host, iri_to_uri(request.get_full_path()))
        if permanent:
            return HttpResponsePermanentRedirect(url)
        else:
            return HttpResponseRedirect(url)

    def request_is_secure(self, request):
        if request.is_secure():
            return True
        elif 'HTTP_X_FORWARDED_SSL' in request.META:
            # Handle forwarded SSL (used at Webfaction)
            return (request.META['HTTP_X_FORWARDED_SSL'] == 'on')
        elif 'HTTP_X_FORWARDED_PROTO' in request.META:
            # Handle forwarded protocol (used at Webfaction)
            return (request.META['HTTP_X_FORWARDED_PROTO'] == 'https')
        elif 'HTTP_X_FORWARDED_HOST' in request.META:
            # Handle an additional case of proxying SSL requests. This is
            # useful for Media Temple's Django container
            return request.META['HTTP_X_FORWARDED_HOST'].endswith('443')
        else:
            return False


class SubdomainsMiddleware(object):

    def process_request(self, request):
        """
        Adds a ``subdomain`` attribute to the request object, which
        corresponds to the portion of the URL before the ``domain`` attribute
        of the current ``Site``.

        If the subdomain is not one of the ``ALLOWED_SUBDOMAINS``, returns an
        ``HttpResponseNotFound`` object.

        """
        site = Site.objects.get_current()
        domain = site.domain
        pattern = r'^(?:(?P<subdomain>.*?)\.)?{0}(?P<addons>.*)$'
        match = re.match(pattern.format(re.escape(domain)),
                         request.get_host())
        if match:
            subdomain = match.group('subdomain')
            addons = match.group('addons')
        else:
            subdomain = ''
            addons = ''

        allowed_subdomains = registry.get('core:ALLOWED_SUBDOMAINS', ())
        if allowed_subdomains and subdomain not in allowed_subdomains:
            return HttpResponseNotFound()

        request.subdomain = subdomain

