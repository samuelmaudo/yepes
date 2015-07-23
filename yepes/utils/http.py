# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from django.utils import six
from django.utils.encoding import force_bytes
from django.utils.six.moves.urllib.parse import (
    quote, quote_plus,
    unquote, unquote_plus,
)


def latin_to_unicode(string):
    if isinstance(string, six.text_type):
        return string
    try:
        return string.decode('latin_1')
    except UnicodeDecodeError:
        return string.decode('utf-8', 'replace')


def get_meta_data(request, key, default=''):
    """
    Extracts metadata from the given ``request`` and encodes them in Unicode.
    """
    return latin_to_unicode(request.META.get(key, default))


def urlquote(url, safe='/'):
    """
    A version of Python's ``urllib.quote()`` function that can operate on
    unicode strings. The url is first UTF-8 encoded before quoting. The
    returned string can safely be used as part of an argument to a subsequent
    ``iri_to_uri()`` call without double-quoting occurring.
    """
    if six.PY3:
        return quote(url, safe)
    else:
        return latin_to_unicode(quote(force_bytes(url), force_bytes(safe)))


def urlquote_plus(url, safe='/'):
    """
    A version of Python's ``urllib.quote_plus()`` function that can operate on
    unicode strings. The url is first UTF-8 encoded before quoting. The
    returned string can safely be used as part of an argument to a subsequent
    ``iri_to_uri()`` call without double-quoting occurring.
    """
    if six.PY3:
        return quote_plus(url, safe)
    else:
        return latin_to_unicode(quote_plus(force_bytes(url), force_bytes(safe)))


def urlunquote(quoted_url):
    """
    A wrapper for Python's ``urllib.unquote()`` function that can operate on
    unicode strings.
    """
    if six.PY3:
        return unquote(quoted_url)
    else:
        return latin_to_unicode(unquote(force_bytes(quoted_url)))


def urlunquote_plus(quoted_url):
    """
    A wrapper for Python's ``urllib.unquote_plus()`` function that can operate
    on unicode strings.
    """
    if six.PY3:
        return unquote_plus(quoted_url)
    else:
        return latin_to_unicode(unquote_plus(force_bytes(quoted_url)))

