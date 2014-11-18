# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from django.utils import six

from yepes.utils.phased import second_pass_render


class PhasedRenderMiddleware(object):
    """
    Middleware that performs a second-phase template rendering on the response.
    """

    def process_response(self, request, response):
        """
        If the content-type starts with ``text/html`` performs a second-phase
        render on response.content and updates the ``Content-Length`` header
        of the response to reflect the change in size after rendering.
        """
        if (not response.streaming
                and response.status_code in (200, 404)
                and response.get('Content-Type', '').startswith('text')):
            response.content = second_pass_render(request, response.content)
            response['Content-Length'] = six.text_type(len(response.content))

        return response

