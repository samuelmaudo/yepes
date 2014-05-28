# -*- coding:utf-8 -*-

import re

from django.utils.encoding import force_text

__all__ = ('css_minifier', 'CssMinifier')

PLACEHOLDER = '~[({{{0}}})]~'

CLOSING_BRACKETS_RE = re.compile(r'\s*;?\s*}\s*')
COLONS_RE = re.compile(r'\s*:\s*')
COMMAS_RE = re.compile(r'\s*,\s*')
COMMENTS_RE = re.compile(r'/\*.*?\*/', re.DOTALL)
NEWLINES_RE = re.compile(r'\s*(\r|\n)\s*')
OPENING_BRACKETS_RE = re.compile(r'\s*{\s*')
PLACEHOLDERS_RE = re.compile(r'\~\[\(\{(\d+)\}\)\]\~')
SEMICOLONS_RE = re.compile(r'\s*;\s*')
WHITESPACES_RE = re.compile(r'[ \t\f\v]+')


class CssMinifier(object):
    """
    Removes all extra whitespaces, comments and other unneeded characters.
    """

    def minify(self, code):
        self.placeholders = []
        return self._minify(force_text(code))

    def _minify(self, code):
        code = self.process_comments(code)
        code = self.process_newlines(code)
        code = self.process_whitespaces(code)
        code = self.process_commas(code)
        code = self.process_opening_brackets(code)
        code = self.process_closing_brackets(code)
        code = self.process_colons(code)
        code = self.process_semicolons(code)
        code = self.fill_placeholders(code)
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

    def process_closing_brackets(self, code):
        return CLOSING_BRACKETS_RE.sub('}\n', code)

    def process_colons(self, code):
        return COLONS_RE.sub(':', code)

    def process_commas(self, code):
        return COMMAS_RE.sub(',', code)

    def process_comments(self, code):
        return COMMENTS_RE.sub('', code)

    def process_newlines(self, code):
        return NEWLINES_RE.sub(r'', code)

    def process_opening_brackets(self, code):
        return OPENING_BRACKETS_RE.sub('{', code)

    def process_semicolons(self, code):
        return SEMICOLONS_RE.sub(';', code)

    def process_whitespaces(self, code):
        return WHITESPACES_RE.sub(' ', code)

    def reserve(self, code):
        self.placeholders.append(code)
        return PLACEHOLDER.format(len(self.placeholders) - 1)

css_minifier = CssMinifier()

