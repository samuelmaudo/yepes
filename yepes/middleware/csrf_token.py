# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from django.middleware.csrf import (
    CsrfViewMiddleware,
    _get_new_csrf_key as generate_csrf_token,
    _sanitize_token as sanitize_csrf_token,
)

from yepes.conf import settings


class CsrfTokenMiddleware(CsrfViewMiddleware):
    """
    Middleware that ensures that all views have a correct ``csrf_token``
    available to ``RequestContext``, but without the CSRF protection that
    ``CsrfViewMiddleware`` enforces.

    Very useful when you need to render forms targeting a view with CSRF
    protection.

    """
    def process_view(self, request, view_func, view_args, view_kwargs):
        if not getattr(request, 'csrf_processing_done', False):
            try:
                # Use same token next time
                token = request.COOKIES[settings.CSRF_COOKIE_NAME]
                request.META['CSRF_COOKIE'] = sanitize_csrf_token(token)
            except KeyError:
                # Generate token and store it in the request, so it's
                # available to the view.
                request.META['CSRF_COOKIE'] = generate_csrf_token()

