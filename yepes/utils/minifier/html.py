# -*- coding:utf-8 -*-

from __future__ import unicode_literals

import re

from django.utils import six
from django.utils.encoding import force_text

from yepes.utils.minifier.css import css_minifier
from yepes.utils.minifier.js import js_minifier

__all__ = ('html_minifier', 'HtmlMinifier')


PLACEHOLDER = '~({{[{0}]}})~'

COMMENTS_RE = re.compile(r'<!--.*?-->', re.DOTALL)
CONDITIONAL_COMMENTS_RE = re.compile(r'(<!--\[[^\]]+\]>)(.*?)(<!\[[^\]]+\]-->)', re.DOTALL)
EMPTY_LINES_RE = re.compile(r'\n{2,}')
LEADING_SPACES_RE = re.compile(r'^ +', re.M)
NEWLINES_RE = re.compile(r'(\r\n|\r)')
PLACEHOLDERS_RE = re.compile(r'\~\(\{\[(\d+)\]\}\)\~')
PRES_RE = re.compile(r'(<pre\b.*?>)(.*?)(<\/pre>)', re.I | re.DOTALL)
SCRIPTS_RE = re.compile(r'(<script\b.*?>)(.*?)(<\/script>)', re.I  | re.DOTALL)
STYLES_RE = re.compile(r'(<style\b.*?>)(.*?)(<\/style>)', re.I | re.DOTALL)
TEXTAREAS_RE = re.compile(r'(<textarea\b.*?>)(.*?)(<\/textarea>)', re.I | re.DOTALL)
TRAILING_SPACES_RE = re.compile(r' +$', re.M)
WHITESPACES_RE = re.compile(r'[ \t\f\v]+')


class HtmlMinifier(object):
    """
    Removes all extra whitespaces, comments and other unneeded characters.

    This class take code from ``html_press`` project.

    """
    def minify(self, code):
        self.placeholders = []
        return self._minify(force_text(code))

    def minify_response(self, response):
        if (not response.streaming
                and response.status_code in (200, 404)
                and response.get('Content-Type', '').startswith('text/html')
                and len(response.content) >= 200):
            response.content = self.minify(response.content)
            response['Content-Length'] = six.text_type(len(response.content))

        return response

    def _minify(self, code):
        code = self.process_newlines(code)
        code = self.process_conditional_comments(code)
        code = self.process_comments(code)
        code = self.process_pres(code)
        code = self.process_textareas(code)
        code = self.process_scripts(code)
        code = self.process_styles(code)
        code = self.process_whitespaces(code)
        code = self.process_leading_spaces(code)
        code = self.process_trailing_spaces(code)
        code = self.process_empty_lines(code)
        code = self.fill_placeholders(code)
        return code

    def conditional_coments_replacement(self, matchobj):
        opening_tag = matchobj.group(1)
        content = self._minify(matchobj.group(2))
        closing_tag = matchobj.group(3)
        return self.reserve(''.join((opening_tag, content, closing_tag)))

    def fill_placeholders(self, code):
        return PLACEHOLDERS_RE.sub(
                self.placeholders_replacement,
                code)

    def placeholders_replacement(self, matchobj):
        try:
            return self.placeholders[int(matchobj.group(1))]
        except IndexError:
            return ''

    def pres_replacement(self, matchobj):
        opening_tag = matchobj.group(1)
        content = self.process_trailing_spaces(matchobj.group(2))
        closing_tag = matchobj.group(3)
        return self.reserve(''.join((opening_tag, content, closing_tag)))

    def process_comments(self, code):
        return COMMENTS_RE.sub('', code)

    def process_conditional_comments(self, code):
        return CONDITIONAL_COMMENTS_RE.sub(
                self.conditional_coments_replacement,
                code)

    def process_empty_lines(self, code):
        return EMPTY_LINES_RE.sub(r'\n', code)

    def process_leading_spaces(self, code):
        return LEADING_SPACES_RE.sub('', code)

    def process_newlines(self, code):
        return NEWLINES_RE.sub(r'\n', code)

    def process_pres(self, code):
        return PRES_RE.sub(
                self.pres_replacement,
                code)

    def process_scripts(self, code):
        return SCRIPTS_RE.sub(
                self.scripts_replacement,
                code)

    def process_styles(self, code):
        return STYLES_RE.sub(
                self.styles_replacement,
                code)

    def process_textareas(self, code):
        return TEXTAREAS_RE.sub(
                self.textareas_replacement,
                code)

    def process_trailing_spaces(self, code):
        return TRAILING_SPACES_RE.sub('', code)

    def process_whitespaces(self, code):
        return WHITESPACES_RE.sub(' ', code)

    def reserve(self, code):
        self.placeholders.append(code)
        return PLACEHOLDER.format(len(self.placeholders) - 1)

    def scripts_replacement(self, matchobj):
        opening_tag = matchobj.group(1)
        content = js_minifier.minify(matchobj.group(2))
        closing_tag = matchobj.group(3)
        return self.reserve(''.join((opening_tag, content, closing_tag)))

    def styles_replacement(self, matchobj):
        opening_tag = matchobj.group(1)
        content = css_minifier.minify(matchobj.group(2))
        closing_tag = matchobj.group(3)
        return self.reserve(''.join((opening_tag, '\n', content, closing_tag)))

    def textareas_replacement(self, matchobj):
        opening_tag = matchobj.group(1)
        content = self.reserve(matchobj.group(2))
        closing_tag = matchobj.group(3)
        return ''.join((opening_tag, content, closing_tag))

html_minifier = HtmlMinifier()

