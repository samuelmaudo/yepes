# -*- coding:utf-8 -*-

from __future__ import unicode_literals

import re
import unicodedata

from django.utils.encoding import force_text
from yepes.utils import unidecode

SPACES_RE = re.compile(r' +')


def slugify(string, extra_characters='', ascii=False, lower=True, spaces=False):
    """
    Returns a copy of the given ``string`` without non-alphanumeric characters.
    Separators, symbols and punctuation characters are replaced by a dash. The
    other characters are simply removed.

    This is a modified version of the eponymous function of the Mozilla
    Foundation to integrate it with the function ``unidecode()``. This
    function generates an ASCII representation of the Unicode characters.
    """
    if ascii:
        string = unidecode(force_text(string))
    else:
        string = unicodedata.normalize('NFKC', force_text(string))

    slug_tokens = []
    for char in string:
        category = unicodedata.category(char)[0]
        # L and N signify letter and number.
        if category in 'LN' or char in extra_characters:
            slug_tokens.append(char)
        # P, S and Z signify punctuation, symbol and separator.
        elif category in 'PSZ':
            slug_tokens.append(' ')

    slug = ''.join(slug_tokens).strip()
    if spaces:
        slug = SPACES_RE.sub(' ', slug)
    else:
        slug = SPACES_RE.sub('-', slug)

    if lower:
        slug = slug.lower()

    return slug

