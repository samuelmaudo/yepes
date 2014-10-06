# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from django.http import (
    HttpResponsePermanentRedirect,
    HttpResponseRedirect,
)
from django.utils.encoding import iri_to_uri

from yepes.conf import settings


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
                        return None

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

