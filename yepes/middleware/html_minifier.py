# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from django import VERSION as DJANGO_VERSION
if DJANGO_VERSION < (1, 10):
    MiddlewareMixin = object
else:
    from django.utils.deprecation import MiddlewareMixin

from yepes.utils.minifier import minify_html_response


class HtmlMinifierMiddleware(MiddlewareMixin):
    """
    Cleans HTML responses by removing all extra whitespaces, comments and other
    unneeded characters.
    """

    def process_response(self, request, response):
        return minify_html_response(response)

