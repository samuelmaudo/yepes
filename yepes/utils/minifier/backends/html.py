# -*- coding:utf-8 -*-

from __future__ import unicode_literals

import re

from yepes.utils.minifier import minify_css, minify_js

__all__ = ('HtmlMinifier', 'minify')


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
WHITESPACES_RE = re.compile(r'[ \t]+')


class HtmlMinifier(object):
    """
    Removes all extra whitespaces, comments and other unneeded characters.

    This class take code from ``html_press`` project.

    """
    def minify(self, code):
        self.placeholders = []
        return self._minify(code)

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
        content = matchobj.group(2)
        closing_tag = matchobj.group(3)
        return ''.join((opening_tag, self.reserve(content), closing_tag))

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
        content = matchobj.group(2)
        if not content.strip():
            content = ''
        else:
            content = minify_js(content)
            if content.endswith('\n'):
                content = ''.join(('\n', content))

        closing_tag = matchobj.group(3)
        return ''.join((opening_tag, self.reserve(content), closing_tag))

    def styles_replacement(self, matchobj):
        opening_tag = matchobj.group(1)
        content = matchobj.group(2)
        if not content.strip():
            content = ''
        else:
            content = minify_css(content)
            if content.endswith('\n'):
                content = ''.join(('\n', content))

        closing_tag = matchobj.group(3)
        return ''.join((opening_tag, self.reserve(content), closing_tag))

    def textareas_replacement(self, matchobj):
        opening_tag = matchobj.group(1)
        content = matchobj.group(2)
        closing_tag = matchobj.group(3)
        return ''.join((opening_tag, self.reserve(content), closing_tag))


def minify(code):
    minifier = HtmlMinifier()
    return minifier.minify(code)

