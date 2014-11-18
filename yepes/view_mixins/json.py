# -*- coding:utf-8 -*-

from __future__ import unicode_literals

import logging

from django.core.exceptions import PermissionDenied, SuspiciousOperation
from django.http import Http404
from django.utils.encoding import force_text
from django.utils import six

from yepes.http import JsonResponse

logger = logging.getLogger('django.request')


class JsonMixin(object):
    """
    Mixin that ensures that the view only returns JSON responses. Additonally,
    includes some methods that can be used to serialize JSON data.
    """

    content_type = None
    force_json_response = False
    response_class = JsonResponse

    def dispatch(self, request, *args, **kwargs):
        """
        Dispatches the request to the appropriate handler and ensures to return
        a JSON response.

        If the handler raises an exception, logs the exception and returns a
        JSON response with the corresponding error code.

        If the handler returns a non-JSON response, creates and returns an
        equivalent JSON response. Unless the response of the handler is a
        success response: in which case, returns a JSON response with the error
        code 501 (Not implemented).

        Adapted from the ``django-jsonview`` decorator authored by James Socol.

        """
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
                'error': {
                    'code': 404,
                    'message': force_text(e),
                },
            }
            return self.response_class(data, status=404)
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
                'error': {
                    'code': 403,
                    'message': force_text(e),
                },
            }
            return self.response_class(data, status=403)
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
                'error': {
                    'code': 400,
                    'message': force_text(e),
                },
            }
            return self.response_class(data, status=400)
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
                'error': {
                    'code': 500,
                    'message': force_text(e),
                },
            }
            return self.response_class(data, status=500)

        if 'json' not in response['Content-Type']:
            if response.status_code == 200:
                data = {
                    'error': {
                        'code': 501,
                        'message': 'Not implemented',
                    },
                }
                return self.response_class(data, status=501)
            else:
                data = {
                    'error': {
                        'code': response.status_code,
                        'message': response.reason_phrase.capitalize(),
                    },
                }
                if response.status_code in (301, 302, 303, 307, 308):
                    data['error']['url'] = response['Location']

                return self.response_class(data, status=response.status_code)

        return response

    def form_invalid(self, form):
        """
        Handles invalid forms by returning a JSON response with the error
        code 484 (Invalid form) and a ``form_errors`` object with the errors
        of the form.

        NOTE: This mixin does not provide a ``form_valid()`` method because
        the standard method returns a redirect response and this type of
        responses are covered by the ``dispatch()`` method.

        WARNING: The status code 484 is not part of the HTTP standard, but I
        not found an appropriate code to indicate invalid forms and I decided
        to use a new code.

        """
        if self.force_json_response or self.request.is_ajax():
            json = self.get_json_data(**{
                'error': {
                    'code': 484,
                    'message': 'Invalid form data',
                },
                'form_errors': {
                    field_name: force_text(error_list[0])
                    for field_name, error_list
                    in six.iteritems(form.errors)
                },
            })
            return self.serialize_to_response(json, status=484)
        else:
            return super(JsonMixin, self).form_invalid(form)

    def get_json_data(self, **kwargs):
        """
        By default, this method simply returns the given kwargs, but can be
        overwritten and therein lies its utility.
        """
        return kwargs

    def serialize_to_response(self, data, **response_kwargs):
        """
        Returns a response, using the ``response_class`` for this view, with
        the given data serialized to a JSON formatted string.
        """
        response_kwargs.setdefault('content_type', self.content_type)
        return self.response_class(data, **response_kwargs)

