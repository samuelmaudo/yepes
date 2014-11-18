# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.utils.encoding import force_text
from django.utils.importlib import import_module

CACHE = {}


def unidecode(string):
    """
    Transliterate Unicode text into plain 7-bit ASCII.

    Example usage:
    >>> from unidecode import unidecode:
    >>> unidecode('\u5317\u4EB0')
    'Bei Jing '

    Take into account that an unicode string object will be returned. If you
    need bytes, use:
    >>> unidecode('Κνωσός').encode('ascii')
    b'Knosos'

    The transliteration uses a straightforward map, and doesn't have
    alternatives for the same character based on language, position, or
    anything else.

    """
    string = force_text(string)
    tokens = []
    for char in string:

        codepoint = ord(char)

        if codepoint < 0x80: # Basic ASCII
            tokens.append(str(char))
            continue

        if codepoint > 0xeffff:
            continue # Characters in Private Use Area and above are ignored

        section = codepoint >> 8   # Chop off the last two hex digits
        position = codepoint % 256 # Last two hex digits

        try:
            table = CACHE[section]
        except KeyError:
            try:
                mod = import_module('.x{0:0>3x}'.format(section), __name__)
            except ImportError:
                CACHE[section] = None
                continue   # No match: ignore this character and carry on.
            else:
                CACHE[section] = table = mod.data

        if table and len(table) > position:
            tokens.append(table[position])

    return ''.join(tokens)
