# -*- coding:utf-8 -*-

from __future__ import unicode_literals

import hashlib

from django.contrib import messages
from django.http import HttpResponsePermanentRedirect
from django.utils.encoding import force_bytes

from yepes.cache import get_mint_cache
from yepes.conf import settings
from yepes.types import Undefined
from yepes.utils.minifier import html_minifier


class CacheMixin(object):

    cache_alias = None
    delay = None
    timeout = None
    use_cache = True

    def __init__(self, *args, **kwargs):
        super(CacheMixin, self).__init__(*args, **kwargs)
        self._cache = get_mint_cache(
            self.cache_alias or settings.VIEW_CACHE_ALIAS,
            timeout=self.timeout or settings.VIEW_CACHE_SECONDS,
            delay=self.delay or settings.VIEW_CACHE_DELAY_SECONDS,
        )

    def get_cache_hash(self, request):
        return '{0}://{1}{2}'.format(
                'https' if request.is_secure() else 'http',
                request.get_host(),
                request.path)

    def get_cache_key(self, request):
        class_name = self.__class__.__name__
        hash = hashlib.md5(force_bytes(self.get_cache_hash(request)))
        return 'yepes.views.{0}.{1}'.format(class_name, hash.hexdigest())

    def dispatch(self, request, *args, **kwargs):
        super_dispatch = super(CacheMixin, self).dispatch
        self.request = request
        self.args = args
        self.kwargs = kwargs
        if (settings.VIEW_CACHE_AVAILABLE
                and self.get_use_cache(request)):

            key = self.get_cache_key(request)
            response = self._cache.get(key)
            if response is None:
                response = super_dispatch(request, *args, **kwargs)
                if response.status_code not in (200, 301, 404):
                    return response

                def update_cache(resp):
                    resp = html_minifier.minify_response(resp)
                    return self._cache.set(key, resp)

                if (hasattr(response, 'render')
                        and callable(response.render)):
                    response.add_post_render_callback(update_cache)
                else:
                    update_cache(response)

            return response
        else:
            return super_dispatch(request, *args, **kwargs)

    def get_use_cache(self, request):
        if (not self.use_cache
                or request.method.upper() not in ('GET', 'HEAD')
                or hasattr(request, 'user') and request.user.is_staff):
            return False
        else:
            return True

