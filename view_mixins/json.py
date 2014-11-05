# -*- coding:utf-8 -*-

from __future__ import unicode_literals

import logging

from django.core.exceptions import PermissionDenied
from django.http import Http404
from django.utils.encoding import force_text

from yepes.http import JsonResponse

logger = logging.getLogger('django.request')


class JsonMixin(object):
    """
    Mixin that ensures that the view will return JSON responses.

    Adapted from the ``django-jsonview`` decorator authored by James Socol.

    """
    force_json_response = False

    def dispatch(self, request, *args, **kwargs):
        if not self.force_json_response and not request.is_ajax():
            return super(JsonMixin, self).dispatch(request, *args, **kwargs)

        try:
            response = super(JsonMixin, self).dispatch(request, *args, **kwargs)
        except Http404 as e:
            logger.warning(
                'Not found: %s',
                request.path,
                extra={
                    'status_code': 404,
                    'request': request,
                },
            )
            data = {
                'error': 404,
                'message': force_text(e)
            }
            return JsonResponse(data, status=404)
        except PermissionDenied as e:
            logger.warning(
                'Forbidden (Permission denied): %s',
                request.path,
                extra={
                    'status_code': 403,
                    'request': request,
                },
            )
            data = {
                'error': 403,
                'message': force_text(e)
            }
            return JsonResponse(data, status=403)
        except SuspiciousOperation as e:
            # The request logger receives events for any problematic request
            # The security logger receives events for all SuspiciousOperations
            security_logger_name = 'django.security.{0}'.format(e.__class__.__name__)
            security_logger = logging.getLogger(security_logger_name)
            security_logger.error(
                force_text(e),
                extra={
                    'status_code': 400,
                    'request': request,
                },
            )
            data = {
                'error': 400,
                'message': force_text(e)
            }
            return JsonResponse(data, status=400)
        except SystemExit:
            # Allow sys.exit() to actually exit.
            raise
        except Exception as e:
            # Handle everything else.
            logger.warning(
                'Internal Server Error: %s',
                request.path,
                extra={
                    'status_code': 500,
                    'request': request,
                },
            )
            data = {
                'error': 500,
                'message': force_text(e)
            }
            return JsonResponse(data, status=500)

        if 'json' in response['Content-Type']:
            return response
        elif response.status_code == 200:
            data = {
                'error': 501,
                'message': 'Not implemented'
            }
            return JsonResponse(data, status=501)
        else:
            data = {
                'error': response.status_code,
                'message': response.reason_phrase.capitalize()
            }
            if response.status_code in (301, 302):
                data['url'] = response.content

            return JsonResponse(data, status=response.status_code)

