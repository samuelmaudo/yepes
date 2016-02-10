# -*- coding:utf-8 -*-

from __future__ import absolute_import, unicode_literals

from pipeline.compressors import CompressorBase

from yepes.utils.minifier import minify_css, minify_js


class Minifier(CompressorBase):
    """
    A compressor that utilizes ``yepes.utils.minifier.minify_css()`` for CSS
    files and ``yepes.utils.minifier.minify_js()`` for JS files.
    """
    def compress_css(self, css):
        return minify_css(css)

    def compress_js(self, js):
        return minify_js(js)

