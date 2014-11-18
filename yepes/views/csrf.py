# -*- coding:utf-8 -*-

from __future__ import unicode_literals

import logging
import sys

from django.views.generic.base import TemplateView

logger = logging.getLogger('django.request')


class CsrfFailureView(TemplateView):

    template_name = 'csrf.html'

    def get(self, request, *args, **kwargs):
        # A CSRF failure is not strictly an error
        # but we want to log it as if it were.
        logger.error('CSRF Failure: %s', request.path,
            exc_info=sys.exc_info(),
            extra={
                'status_code': 403,
                'request': request,
            }
        )
        return super(CsrfFailureView, self).get(request, *args, **kwargs)

    def post(self, *args, **kwargs):
        return self.get(*args, **kwargs)

    def put(self, *args, **kwargs):
        return self.get(*args, **kwargs)

csrf_failure_view = CsrfFailureView.as_view()

