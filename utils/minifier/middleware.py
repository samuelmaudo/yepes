# -*- coding:utf-8 -*-

from yepes.utils.minifier.html import html_minifier


class HtmlMinifierMiddleware(object):
    """
    Cleans the response content.
    """

    def process_response(self, request, response):
        """
        Removes all extra whitespaces, comments and other unneeded characters.
        """
        return html_minifier.minify_response(response)

