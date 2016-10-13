# -*- coding:utf-8 -*-

from __future__ import unicode_literals

import collections
import re

from django.utils import six
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe
from django.utils.six import unichr as chr
from django.utils.six.moves.html_parser import HTMLParser

from yepes.utils.htmlentities import ENTITIES_TO_CHARACTERS

__all__ = ('close_tags', 'extract_text')

BLANK_LINES_RE = re.compile(r'\n\s+\n')
SPACES_RE = re.compile(r'\s+')

BOOLEAN_ATTRS = {
    'allowfullscreen',
    'async',
    'autofocus',
    'autoplay',
    'checked',
    'compact',
    'controls',
    'declare',
    'default',
    'defaultchecked',
    'defaultmuted',
    'defaultselected',
    'defer',
    'disabled',
    'download',
    'draggable',
    'enabled',
    'formnovalidate',
    'hidden',
    'indeterminate',
    'inert',
    'ismap',
    'itemscope',
    'loop',
    'mozallowfullscreen',
    'multiple',
    'muted',
    'nohref',
    'noresize',
    'noshade',
    'novalidate',
    'nowrap',
    'open',
    'pauseonexit',
    'ping',
    'readonly',
    'required',
    'reversed',
    'scoped',
    'seamless',
    'selected',
    'sortable',
    'spellcheck',
    'translate',
    'truespeed',
    'typemustmatch',
    'visible',
    'webkitallowfullscreen',
}

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


def make_double_tag(name, content='', attrs=None):
    """
    Makes a HTML tag with its end tag. The content and the values of the
    attributes are passed through ``conditional_escape()`` and the result is
    marked as safe.
    """
    start_tag = make_single_tag(name, attrs)
    end_tag = '</{0}>'.format(name)
    return mark_safe(''.join((start_tag, conditional_escape(content), end_tag)))


def make_single_tag(name, attrs=None):
    """
    Makes an empty HTML tag which means that it has no end tag. The values
    of the attributes are passed through ``conditional_escape()`` and the
    result is marked as safe.
    """
    if attrs:

        if isinstance(attrs, collections.Mapping):
            iterator = six.iteritems(attrs)
        else:
            iterator = iter(attrs)

        attributes = []
        booleans = BOOLEAN_ATTRS
        for key, value in iterator:

            if key == 'cls':
                # 'class' is a reserved word in Python so, if you
                # want to set the attributes as keyword arguments,
                # you cannot use it.
                key = 'class'

            if key.lower() not in booleans:
                attributes.append('{0}="{1}"'.format(key, conditional_escape(value)))
            elif value:
                attributes.append(key)

        tag = '<{0} {1}>'.format(name, ' '.join(attributes))
    else:
        tag = '<{0}>'.format(name)

    return mark_safe(tag)


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
        elif tag == 'abbr':
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

