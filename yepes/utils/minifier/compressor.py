# -*- coding:utf-8 -*-

from __future__ import absolute_import, unicode_literals

from compressor.filters import FilterBase

from yepes.utils.minifier import minify_css, minify_js


class CssMinifier(FilterBase):
    """
    A CSS filter that utilizes ``yepes.utils.minifier.minify_css()``.
    """
    def output(self, **kwargs):
        return minify_css(self.content)


class JsMinifier(FilterBase):
    """
    A JS filter that utilizes ``yepes.utils.minifier.minify_js()``.
    """
    def output(self, **kwargs):
        return minify_js(self.content)

