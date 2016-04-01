# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from django.core.exceptions import ImproperlyConfigured
from django.http import HttpResponsePermanentRedirect


class CanonicalMixin(object):

    canonical_path = None
    check_canonical = True

    def dispatch(self, request, *args, **kwargs):
        if self.get_check_canonical(request):
            path = self.get_canonical_path(request)
            if request.path != path:
                url = path
                query = request.META.get('QUERY_STRING', '')
                if query:
                    url = '{0}?{1}'.format(url, query)

                return HttpResponsePermanentRedirect(url)

        return super(CanonicalMixin, self).dispatch(request, *args, **kwargs)

    def get_canonical_path(self, request):
        if self.canonical_path is None:
            msg = (
                "CanonicalMixin requires either a definition of "
                "'canonical_path' or an implementation of "
                "'get_canonical_path()'"
            )
            raise ImproperlyConfigured(msg)
        else:
            return self.canonical_path

    def get_check_canonical(self, request):
        return self.check_canonical

