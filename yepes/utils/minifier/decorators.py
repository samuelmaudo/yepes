# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from functools import update_wrapper

from yepes.utils.minifier import minify_css, minify_html, minify_js


def minify_css_output(function):
    """
    A decorator that minifies the CSS output of any function that it decorates.
    """
    def wrapper(*args, **kwargs):
        return minify_css(function(*args, **kwargs))

    update_wrapper(wrapper, function)
    return wrapper


def minify_html_output(function):
    """
    A decorator that minifies the HTML output of any function that it decorates.
    """
    def wrapper(*args, **kwargs):
        return minify_html(function(*args, **kwargs))

    update_wrapper(wrapper, function)
    return wrapper


def minify_js_output(function):
    """
    A decorator that minifies the JS output of any function that it decorates.
    """
    def wrapper(*args, **kwargs):
        return minify_js(function(*args, **kwargs))

    update_wrapper(wrapper, function)
    return wrapper

