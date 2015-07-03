# -*- coding:utf-8 -*-

from __future__ import unicode_literals

import re

from django.utils.six import unichr as chr
from django.utils.six.moves.html_parser import HTMLParser

from yepes.utils.htmlentities import ENTITIES_TO_CHARACTERS

__all__ = ('close_tags', 'extract_text')

BLANK_LINES_RE = re.compile(r'\n\s+\n')
SPACES_RE = re.compile(r'\s+')

SELF_CLOSING_TAGS = {
    'area',
    'base',
    'br',
    'col',
    'command',
    'embed',
    'hr',
    'img',
    'input',
    'keygen',
    'link',
    'meta',
    'param',
    'source',
    'track',
    'wbr',
}


def close_tags(html):
    """
    Adds a closing tag for each unclosed tag in ``html``.
    """
    parser = OpenTagsParser()
    parser.feed(html)
    open_tags = parser.get_result()
    return html + ''.join('</{0}>'.format(tag) for tag in open_tags)


def extract_text(html):
    """
    Extracts plain text from given ``html``.

    This function is similar to ``django.utils.html.strip_tags()`` but also
    converts HTML entities into unicode characters.

    """
    parser = TextFragmentsParser()
    parser.feed(html)
    text = ''.join(parser.get_result())
    return BLANK_LINES_RE.sub('\n\n', text).strip()


class OpenTagsParser(HTMLParser):
    """
    HTMLParser that returns unclosed tags in reverse order.
    """
    def __init__(self, *args, **kwargs):
        HTMLParser.__init__(self, *args, **kwargs)
        self.open_tags = []

    def get_result(self):
        return self.open_tags

    def handle_endtag(self, tag):
        try:
            self.open_tags.remove(tag)
        except ValueError:
            pass

    def handle_starttag(self, tag, attrs):
        if tag not in SELF_CLOSING_TAGS:
            self.open_tags.insert(0, tag)


class TextFragmentsParser(HTMLParser):
    """
    HTMLParser that returns all pieces of text.
    """
    def __init__(self, *args, **kwargs):
        HTMLParser.__init__(self, *args, **kwargs)
        self.is_idle = 0
        self.last_abbr = None
        self.last_link = None
        self.text_fragments = []

    def _append(self, token):
        if not self.is_idle:
            self.text_fragments.append(token)

    def get_result(self):
        return self.text_fragments

    def handle_charref(self, name):
        if name.startswith(('x', 'X')):
            char = chr(int(name[1:], 16))
        else:
            char = chr(int(name))
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

