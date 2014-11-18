# -*- coding:utf-8 -*-

from __future__ import unicode_literals

import re

from django.utils.six import unichr
from django.utils.six.moves import html_parser

from yepes.utils.minifier import html_minifier
from yepes.utils.htmlentities import ENTITIES_TO_CHARACTERS

__all__ = ('html2text', )

BLANK_LINES_RE = re.compile(r'\n\s+\n')
SPACES_RE = re.compile(r'\s+')


class Html2TextParser(html_parser.HTMLParser):

    def __init__(self, *args, **kwargs):
        html_parser.HTMLParser.__init__(self, *args, **kwargs)
        self.is_idle = 0
        self.last_abbr = None
        self.last_link = None
        self.text_tokens = []

    def _append(self, token):
        if not self.is_idle:
            self.text_tokens.append(token)

    def get_result(self):
        text = ''.join(self.text_tokens)
        return BLANK_LINES_RE.sub('\n\n', text).strip()

    def handle_charref(self, name):
        if name.startswith(('x', 'X')):
            char = unichr(int(name[1:], 16))
        else:
            char = unichr(int(name))
        if char is not None:
            self._append(char)

    def handle_data(self, data):
        self._append(SPACES_RE.sub(' ', data))

    def handle_endtag(self, tag):
        if tag == 'a':
            if self.last_link:
                self._append(' ({0})'.format(self.last_link))
                self.last_link = None
        elif tag == 'abbr':
            if self.last_abbr:
                self._append(' ({0})'.format(self.last_abbr))
                self.last_abbr = None
        elif tag in ('head', 'style', 'script'):
            self.is_idle -= 1
        elif tag in ('ol', 'ul', 'dl', 'dd'):
            self._append('\n')
        elif tag in ('p', 'div', 'table'):
            self._append('\n\n')

    def handle_entityref(self, name):
        char = ENTITIES_TO_CHARACTERS.get(name)
        if char is not None:
            self._append(char)

    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            for attr, value in attrs:
                if attr == 'href' and value:
                    self.last_link = value
                    break
        if tag == 'abbr':
            for attr, value in attrs:
                if attr == 'title' and value:
                    self.last_abbr = value
                    break
        elif tag == 'body':
            self.is_idle = 0
        elif tag == 'br':
            self._append('\n')
        elif tag == 'dd':
            self._append('\n    ')
        elif tag in ('del', 'strike', 's'):
            pass
        elif tag in ('head', 'style', 'script'):
            self.is_idle += 1
        elif tag == 'hr':
            self._append('\n******\n')
        elif tag == 'li':
            self._append('\n*   ')
        elif tag in ('ol', 'ul', 'dl', 'dt', 'th', 'tr'):
            self._append('\n')
        elif tag in ('p', 'div', 'table'):
            self._append('\n\n')


def html2text(html):
    parser = Html2TextParser()
    parser.feed(html_minifier.minify(html or ''))
    return parser.get_result()

