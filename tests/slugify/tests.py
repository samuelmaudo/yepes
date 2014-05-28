# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from django import test

from yepes.utils import slugify


class SlugifyTest(test.SimpleTestCase):

    def checkSlug(self, tests):
        for string, slug in tests:
            self.assertEqual(slugify(string), slug)

    def test_usage(self):
        a = 'Ελληνικά'
        b = b'-'.join((a, a))
        c = b' - '.join((a, a))
        self.checkSlug([
            (b'xx x  - "#$@ x',
             b'xx-x-x'),
            ('Bän...g (bang)',
             'bän-g-bang'),
            (a,
             a.lower()),
            (b,
             b.lower()),
            (c,
             b.lower()),
            (b'    a ',
             b'a'),
            (b'tags/',
             b'tags'),
            (b'holy_wars',
             b'holy-wars'),

            # Make sure we get a consistent result with decomposed chars:
            ('el ni\N{LATIN SMALL LETTER N WITH TILDE}o',
             'el-ni\xf1o'),
            ('el nin\N{COMBINING TILDE}o',
             'el-ni\xf1o'),

            # Ensure we normalize appearance-only glyphs into their
            # compatibility forms:
            ('\N{LATIN SMALL LIGATURE FI}lms',
             'films'),

            # I don't really care what slugify returns.  Just don't crash.
            ('x𘍿',
             'x'),
            ('ϧ΃𘒬𘓣',
             '\u03e7'),
            ('¿x',
             'x'),
        ])

