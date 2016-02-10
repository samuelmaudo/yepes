# -*- coding:utf-8 -*-

from __future__ import unicode_literals

import re

__all__ = ('CssMinifier', 'minify')

PLACEHOLDER = '~[({{{0}}})]~'

CLOSING_BRACKETS_RE = re.compile(r'\s*;?\s*}\s*')
COLONS_RE = re.compile(r'\s*:\s*')
COMMAS_RE = re.compile(r'\s*,\s*')
COMMENTS_RE = re.compile(r'/\*.*?\*/', re.DOTALL)
NEWLINES_RE = re.compile(r'\s*[\r\n]\s*')
OPENING_BRACKETS_RE = re.compile(r'\s*{\s*')
PLACEHOLDERS_RE = re.compile(r'\~\[\(\{(\d+)\}\)\]\~')
SELECTORS_RE = re.compile(r'(\A|\})(.*?)(\{)', re.DOTALL)
SEMICOLONS_RE = re.compile(r'\s*;\s*')
WHITESPACES_RE = re.compile(r'[ \t]+')
ZEROS_RE = re.compile(r'(?<=[:\s])0+(\.\d+)')


class CssMinifier(object):
    """
    Removes all extra whitespaces, comments and other unneeded characters.
    """

    def minify(self, code):
        self.placeholders = []
        return self._minify(code)

    def _minify(self, code):
        code = self.process_comments(code)
        code = self.process_newlines(code)
        code = self.process_whitespaces(code)
        code = self.process_commas(code)
        code = self.process_opening_brackets(code)
        code = self.process_closing_brackets(code)
        code = self.process_semicolons(code)
        code = self.reserve_selectors(code)
        code = self.process_colons(code)
        code = self.process_zeros(code)
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

    def process_zeros(self, code):
        return ZEROS_RE.sub('\1', code)

    def reserve(self, code):
        self.placeholders.append(code)
        return PLACEHOLDER.format(len(self.placeholders) - 1)

    def reserve_selectors(self, code):
        return SELECTORS_RE.sub(
                self.selectors_replacement,
                code)

    def selectors_replacement(self, matchobj):
        opening_bracket = matchobj.group(1)
        content = self.reserve(matchobj.group(2))
        closing_bracket = matchobj.group(3)
        return ''.join((opening_bracket, content, closing_bracket))


def minify(code):
    minifier = CssMinifier()
    return minifier.minify(code)

