# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from yepes.utils.minifier.html import html_minifier


class HtmlMinifierMiddleware(object):
    """
    Cleans HTML responses by removing all extra whitespaces, comments and other
    unneeded characters.
    """

    def process_response(self, request, response):
        return html_minifier.minify_response(response)

