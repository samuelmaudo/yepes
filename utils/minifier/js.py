# -*- coding:utf-8 -*-

import re

from django.utils.encoding import force_text

__all__ = ('js_minifier', 'JsMinifier')

PLACEHOLDER = '~{{[({0})]}}~'

COMMENTS_RE = re.compile(r'// .*?')
EMPTY_LINES_RE = re.compile(r'\n{2,}')
LEADING_SPACES_RE = re.compile(r'^ +', re.M)
MULTI_LINE_COMMENTS_RE = re.compile(r'/\*.*?\*/', re.DOTALL)
NEWLINES_RE = re.compile(r'(\r\n|\r)')
PLACEHOLDERS_RE = re.compile(r'\~\{\[\((\d+)\)\]\}\~')
TRAILING_SPACES_RE = re.compile(r' +$', re.M)
WHITESPACES_RE = re.compile(r'[ \t\f\v]+')


class JsMinifier(object):
    """
    Removes all extra whitespaces, comments and other unneeded characters.
    """

    def minify(self, code):
        self.placeholders = []
        return self._minify(force_text(code))

    def _minify(self, code):
        code = self.process_newlines(code)
        #code = self.process_comments(code)
        code = self.process_whitespaces(code)
        code = self.process_leading_spaces(code)
        code = self.process_trailing_spaces(code)
        code = self.process_empty_lines(code)
        #code = self.fill_placeholders(code)
        return code

    def fill_placeholders(self, code):
        return PLACEHOLDERS_RE.sub(
                self.placeholders_replacement,
                code)

    def placeholders_replacement(self, matchobj):
        try:
            return self.placeholders[int(matchobj.group(1))]
        except IndexError:
            return ''

    def process_comments(self, code):
        code = COMMENTS_RE.sub('', code)
        code = MULTI_LINE_COMMENTS_RE.sub('', code)
        return code

    def process_empty_lines(self, code):
        return EMPTY_LINES_RE.sub(r'\n', code)

    def process_leading_spaces(self, code):
        return LEADING_SPACES_RE.sub('', code)

    def process_newlines(self, code):
        return NEWLINES_RE.sub(r'\n', code)

    def process_trailing_spaces(self, code):
        return TRAILING_SPACES_RE.sub('', code)

    def process_whitespaces(self, code):
        return WHITESPACES_RE.sub(' ', code)

    def reserve(self, code):
        self.placeholders.append(code)
        return PLACEHOLDER.format(len(self.placeholders) - 1)

js_minifier = JsMinifier()

