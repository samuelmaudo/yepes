# -*- coding:utf-8 -*-

from django.utils import six
from django.utils.encoding import force_text

from yepes.conf import settings
from yepes.utils.minifier.backends import get_backend


def minify_css(code):
    return get_backend(settings.CSS_MINIFIER)(force_text(code))


def minify_html(code):
    return get_backend(settings.HTML_MINIFIER)(force_text(code))


def minify_html_response(response):
    if (not response.streaming
            and response.status_code in (200, 404)
            and response.get('Content-Type', '').startswith('text/html')
            and len(response.content) >= 200):
        response.content = minify_html(response.content)
        response['Content-Length'] = six.text_type(len(response.content))

    return response


def minify_js(code):
    return get_backend(settings.JS_MINIFIER)(force_text(code))

