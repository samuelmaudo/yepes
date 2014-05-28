# -*- coding:utf-8 -*-

from __future__ import unicode_literals

import sys

from django import test
from django.utils.unittest import skipIf

from yepes.utils import unidecode


class UnidecodeTest(test.SimpleTestCase):

    def checkUnidecode(self, tests):
        for unicode, ascii in tests:
            self.assertEqual(unidecode(unicode), ascii)

    def test_ascii(self):
        for n in xrange(0, 128):
            self.assertEqual(
                unidecode(unichr(n)),
                unichr(n),
            )

    def test_bmp(self):
        # Just check that it doesn't throw an exception
        for n in xrange(0, 0x10000):
            unidecode(unichr(n))

    def test_circled_latin(self):
        # 1 sequence of a-z
        for n in xrange(0, 26):
            self.assertEqual(
                unidecode(unichr(0x24d0 + n)),
                unichr(ord('a') + n),
            )

    @skipIf(sys.maxunicode < 0x10000, 'Narrow build.')
    def test_mathematical_latin(self):
        # 13 consecutive sequences of A-Z, a-z with some codepoints
        # undefined. We just count the undefined ones and don't check
        # positions.
        empty_count = 0
        for n in xrange(0x1d400, 0x1d6a4):
            a = unidecode(unichr(n))
            if n % 52 < 26:
                b = unichr(ord('A') + n % 26)
            else:
                b = unichr(ord('a') + n % 26)
            if not a:
                empty_count += 1
            else:
                self.assertEqual(a, b)

        self.assertEqual(empty_count, 24)

    @skipIf(sys.maxunicode < 0x10000, 'Narrow build.')
    def test_mathematical_digits(self):
        # 5 consecutive sequences of 0-9
        for n in xrange(0x1d7ce, 0x1d800):
            self.assertEqual(
                unidecode(unichr(n)),
                unichr(ord('0') + (n-0x1d7ce) % 10),
            )

    def test_usage(self):
        self.checkUnidecode([
            ('Hello, World!',
             'Hello, World!'),
            ('"\'\r\n',
             '"\'\r\n'),
            ('Ελληνικά',
             'Ellenika'),
            ('ČŽŠčžš',
             'CZSczs'),
            ('ア',
             'a'),
            ('α',
             'a'),
            ('а',
             'a'),
            ('ch\xe2teau',
             'chateau'),
            ('vi\xf1edos',
             'vinedos'),
            ('\u5317\u4EB0',
             'Bei Jing '),
            ('Efﬁcient',
             'Efficient'),

            # https://github.com/iki/unidecode/commit/4a1d4e0a7b5a11796dc701099556876e7a520065
            ('příliš žluťoučký kůň pěl ďábelské ódy',
             'prilis zlutoucky kun pel dabelske ody'),
            ('PŘÍLIŠ ŽLUŤOUČKÝ KŮŇ PĚL ĎÁBELSKÉ ÓDY',
             'PRILIS ZLUTOUCKY KUN PEL DABELSKE ODY'),

            # Table that doesn't exist
            ('\ua500',
             ''),

            # Table that has less than 256 entriees
            ('\u1eff',
             ''),
        ])

    @skipIf(sys.maxunicode < 0x10000, 'Narrow build.')
    def test_usage_wide(self):
        self.checkUnidecode([
            # Non-BMP character
            ('\U0001d5a0',
             'A'),

            # Mathematical
            ('\U0001d5c4\U0001d5c6/\U0001d5c1',
             'km/h'),
        ])

