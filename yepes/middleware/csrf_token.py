# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from django import VERSION as DJANGO_VERSION
from django.middleware.csrf import CsrfViewMiddleware
from django.middleware.csrf import _sanitize_token as sanitize_csrf_token
if DJANGO_VERSION < (1, 10):
    from django.middleware.csrf import _get_new_csrf_key as generate_csrf_token
else:
    from django.middleware.csrf import _get_new_csrf_token as generate_csrf_token

from yepes.conf import settings


class CsrfTokenMiddleware(CsrfViewMiddleware):
    """
    Middleware that ensures that all views have a correct ``csrf_token``
    available to ``RequestContext``, but without the CSRF protection that
    ``CsrfViewMiddleware`` enforces.

    Very useful when you need to render forms targeting a view with CSRF
    protection.

    """
    def process_view(self, request, callback, callback_args, callback_kwargs):
        if getattr(request, 'csrf_processing_done', False):
            return None

        try:
            # Use same token next time
            token = request.COOKIES[settings.CSRF_COOKIE_NAME]
            request.META['CSRF_COOKIE'] = sanitize_csrf_token(token)
        except KeyError:
            # Generate token and store it in the request, so it's
            # available to the view.
            request.META['CSRF_COOKIE'] = generate_csrf_token()

        return self._accept(request)

