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

__all__ = ('CacheMixin', 'CanonicalMixin', 'MessageMixin', 'ModelMixin')


class CacheMixin(object):

    delay_seconds = None
    timeout = None
    use_cache = True

    def __init__(self, *args, **kwargs):
        self._cache = get_mint_cache(settings.VIEW_CACHE_ALIAS, **{
            'timeout': self.timeout or settings.VIEW_CACHE_SECONDS,
            'delay': self.delay_seconds or settings.VIEW_CACHE_DELAY_SECONDS,
        })
        super(CacheMixin, self).__init__(*args, **kwargs)

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
                or request.user.is_staff
                or request.method.upper() not in ('GET', 'HEAD')):
            return False
        else:
            return True


class CanonicalMixin(object):

    check_canonical = True

    def dispatch(self, request, *args, **kwargs):
        if self.get_check_canonical(request):
            canonical_path = self.get_canonical_url()
            if self.request.path != canonical_path:
                return HttpResponsePermanentRedirect(canonical_path)
        return super(CanonicalMixin, self).dispatch(request, *args, **kwargs)

    def get_canonical_url(self):
        return self.get_object().get_absolute_url()

    def get_check_canonical(self, request):
        return self.check_canonical


class MessageMixin(object):

    leave_message = False
    success_message = None

    def get_leave_message(self, request):
        return self.leave_message

    def get_success_message(self, request):
        if self.success_message:
            return self.success_message
        else:
            msg = "No message to leave. Provide a ``success_message``."
            raise ImproperlyConfigured(msg)

    def send_success_message(self, request):
        if self.get_leave_message(request):
            msg = self.get_success_message(request)
            messages.success(request, msg)


class ModelMixin(object):

    _model = Undefined

    def get_model(self):
        if self._model is Undefined:
            # If a model has been explicitly provided, use it.
            if getattr(self, 'model', None) is not None:
                self._model = self.model

            # If this view is operating on a single object, use the class
            # of that object.
            elif getattr(self, 'object', None) is not None:
                self._model = self.object.__class__

            # If this view is operating on a list of objects, try to get
            # the model class from that.
            elif (getattr(self, 'object_list', None) is not None
                    and getattr(self, 'model', None) is not None):
                self._model = self.object_list.model

            # Try to get a queryset and extract the model class from that.
            else:
                qs = self.get_queryset()
                if getattr(qs, 'model', None) is not None:
                    self._model = qs.model
                else:
                    self._model = None

        return self._model

