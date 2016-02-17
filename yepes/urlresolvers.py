# -*- coding:utf-8 -*-

import re

from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse as reverse
from django.utils import six
from django.utils.encoding import iri_to_uri
from django.utils.functional import lazy

from yepes.conf import settings
from yepes.contrib.registry import registry

__all__ = ('build_full_url', 'full_reverse', 'full_reverse_lazy')

FULL_URL_RE = re.compile(r'^[a-z][a-z0-9.-]+:', re.IGNORECASE)


def build_full_url(location, scheme=None, domain=None, subdomain=None):
    """
    Adds the scheme name and the authority part (domain and subdomain) to the
    given absolute path.

    Args::

        location (str): Absolute resource path.

        scheme (str): Scheme name (commonly called protocol).

        domain (str): Domain name.

        subdomain (str): Subdomain name.

    Returns::

        The uniform resource locator of the given absolute path.

    Examples::

        >>> build_full_url('/clients/client/123/')
        'http://example.com/clients/client/123/'

        >>> build_full_url('/clients/', scheme='https', subdomain='admin')
        'https://admin.example.com/clients/'

    """
    if FULL_URL_RE.match(location):
        return iri_to_uri(location)

    if not scheme:
        if settings.SSL_ENABLED:
            for path in settings.SSL_PATHS:
                if location.startswith(path):
                    scheme = 'https'
                    break
            else:
                scheme = 'http'
        else:
            scheme = 'http'

    domain = domain or Site.objects.get_current().domain
    subdomain = subdomain or registry.get('core:DEFAULT_SUBDOMAIN', '')
    if subdomain:
        url = '{0}://{1}.{2}{3}'.format(scheme, subdomain, domain, location)
    else:
        url = '{0}://{1}{2}'.format(scheme, domain, location)

    return iri_to_uri(url)


def full_reverse(viewname, urlconf=None, args=None, kwargs=None, prefix=None,
                 current_app=None, scheme=None, domain=None, subdomain=None):
    """
    First, obtains the absolute path of the URL matching given ``viewname``
    with its parameters.

    Then, prepends the path with the scheme name and the authority part (domain
    and subdomain) and returns it.

    Args::

        viewname (str): Name of the URL pattern.

        urlconf (str): Path of the module containing URLconfs.

        args (list): Positional arguments of the URL pattern.

        kwargs (dict): Keyword arguments of the URL pattern.

        prefix (str): Prefix of the URL pattern.

        current_app (str): App identifier.

        scheme (str): Scheme name (commonly called protocol).

        domain (str): Domain name.

        subdomain (str): Subdomain name.

    Returns::

        The full URL matching given view with its parameters.

    Examples::

        >>> full_reverse('client-detail-view', args=[client.id])
        'http://example.com/clients/client/123/'

        >>> full_reverse('client-list-view', scheme='https', subdomain='admin')
        'https://admin.example.com/clients/'

    Raises::

        NoReverseMatch: If no URL pattern matches the given ``viewname``.

        ValueError: If both ``args`` and ``kwargs`` are given.

    """
    location = reverse(viewname, urlconf, args, kwargs, prefix, current_app)
    return build_full_url(location, scheme, domain, subdomain)


full_reverse_lazy = lazy(full_reverse, six.text_type)

