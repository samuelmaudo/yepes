# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from django.http import HttpResponsePermanentRedirect


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

