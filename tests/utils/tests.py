# -*- coding:utf-8 -*-

from __future__ import unicode_literals

import collections
from datetime import datetime
from decimal import Decimal
import random
import sys
import traceback
import warnings

from django import test
from django.utils.six import unichr as chr
from django.utils.six.moves import range
from django.utils.unittest import skipIf

from yepes.utils import (
    decimals,
    emails,
    formats,
    html,
    htmlentities,
    iterators,
    minifier,
    modules,
    properties,
    slugify,
    unidecode,
)
from yepes.utils.minifier import decorators as minifier_decorators


class DecimalsTest(test.SimpleTestCase):

    def test_force_decimal(self):
        self.assertEqual(
            decimals.force_decimal('7'),
            Decimal('7'),
        )
        self.assertEqual(
            decimals.force_decimal(7),
            Decimal('7'),
        )
        self.assertEqual(
            decimals.force_decimal(7.0),
            Decimal('7'),
        )
        self.assertEqual(
            decimals.force_decimal(Decimal('7')),
            Decimal('7'),
        )

    def test_round_decimal(self):
        self.assertEqual(
            repr(decimals.round_decimal(7.5, 0)),
            "Decimal('8')",
        )
        self.assertEqual(
            repr(decimals.round_decimal(7, 2)),
            "Decimal('7.00')",
        )
        self.assertEqual(
            repr(decimals.round_decimal(7, exponent=Decimal('0.00'))),
            "Decimal('7.00')",
        )

    def test_sum_decimals(self):
        result = decimals.sum_decimals([Decimal('4'), Decimal('3.50')])
        self.assertIsInstance(
            result,
            Decimal,
        )
        self.assertEqual(
            result,
            Decimal('7.5'),
        )
        self.assertEqual(
            repr(result),
            "Decimal('7.50')",
        )


class EmailTest(test.SimpleTestCase):

    def test_normalize_email(self):
        self.assertEqual(
            emails.normalize_email('john.smith@example.com'),
            'john.smith@example.com',
        )
        self.assertEqual(
            emails.normalize_email('JOHN.SMITH@EXAMPLE.COM'),
            'john.smith@example.com',
        )
        self.assertEqual(
            emails.normalize_email('John.Smith@Example.Com'),
            'John.Smith@example.com',
        )

    def test_validate_email(self):
        # Valid and common.
        self.assertTrue(emails.validate_email('niceandsimple@example.com'))
        self.assertTrue(emails.validate_email('very.common@example.com'))
        self.assertTrue(emails.validate_email('a.little.lengthy.but.fine@dept.example.com'))
        self.assertTrue(emails.validate_email('disposable.style.email.with+symbol@example.com'))
        self.assertTrue(emails.validate_email('other.email-with-dash@example.com'))
        # Valid according to standard but uncommon.
        self.assertFalse(emails.validate_email(r'"much.more unusual"@example.com'))
        self.assertFalse(emails.validate_email(r'"very.unusual.@.unusual.com"@example.com'))
        self.assertFalse(emails.validate_email(r'"very.(),:;<>[]\".VERY.\"very@\\ \"very\".unusual"@strange.example.com'))
        self.assertFalse(emails.validate_email(r'admin@mailserver1'))
        self.assertFalse(emails.validate_email(r'jsmith@[192.168.2.1'))
        self.assertFalse(emails.validate_email(r'jsmith@[IPv6:2001:db8::1]'))
        self.assertFalse(emails.validate_email(r"#!$%&'*+-/=?^_`{}|~@example.org"))
        self.assertFalse(emails.validate_email(r'"()<>[]:,;@\\\"!#$%&\'*+-/=?^_`{}| ~.a"@example.org'))
        self.assertFalse(emails.validate_email(r'" "@example.org'))
        self.assertFalse(emails.validate_email(r'üñîçøðé@example.com'))
        self.assertFalse(emails.validate_email(r'üñîçøðé@üñîçøðé.com'))
        # Not valid.
        self.assertFalse(emails.validate_email(r'Abc.example.com'))
        self.assertFalse(emails.validate_email(r'A@b@c@example.com'))
        self.assertFalse(emails.validate_email(r'a"b(c)d,e:f;g<h>i[j\k]l@example.com'))
        self.assertFalse(emails.validate_email(r'just"not"right@example.com'))
        self.assertFalse(emails.validate_email(r'this is"not\allowed@example.com'))
        self.assertFalse(emails.validate_email(r'this\ still\"not\\allowed@example.com'))
        self.assertFalse(emails.validate_email(r'john..doe@example.com'))
        self.assertFalse(emails.validate_email(r'john.doe@example..com'))


class FormatsTest(test.SimpleTestCase):

    def test_permissive_date_format(self):
        self.assertEqual(
            formats.permissive_date_format(None, 'SHORT_DATE_FORMAT'),
            '00/00/0',
        )
        self.assertEqual(
            formats.permissive_date_format(None, 'SHORT_DATETIME_FORMAT'),
            '00/00/0 midnight',
        )
        self.assertEqual(
            formats.permissive_date_format(datetime(2010, 3, 1), 'SHORT_DATE_FORMAT'),
            '03/01/2010',
        )
        self.assertEqual(
            formats.permissive_date_format(datetime(2010, 3, 1, 12, 30), 'SHORT_DATETIME_FORMAT'),
            '03/01/2010 12:30 p.m.',
        )


class IteratorsTest(test.SimpleTestCase):

    def test_isplit(self):
        result = iterators.isplit([1, 2, 3, 4, 5, 6, 7], 3)
        self.assertIsInstance(result, collections.Iterator)
        self.assertEqual(
            list(result),
            [[1, 2, 3], [4, 5, 6], [7]]
        )
        iterable = iter([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
        self.assertEqual(
            next(iterators.isplit(iterable, 1)),
            [1],
        )
        self.assertEqual(
            next(iterators.isplit(iterable, 2)),
            [2, 3],
        )
        self.assertEqual(
            next(iterators.isplit(iterable, 3)),
            [4, 5, 6],
        )
        self.assertEqual(
            list(iterable),
            [7, 8, 9, 10],
        )

    def test_split(self):
        result = iterators.split([1, 2, 3, 4, 5, 6, 7], 3)
        self.assertIsInstance(result, collections.MutableSequence)
        self.assertEqual(
            result,
            [[1, 2, 3], [4, 5, 6], [7]]
        )


class HtmlTest(test.SimpleTestCase):

    def test_close_tags(self):
        self.assertEqual(
            html.close_tags('<p><strong>Lorem fistrum</strong> pecador.'),
            '<p><strong>Lorem fistrum</strong> pecador.</p>',
        )
        self.assertEqual(
            html.close_tags('<p><em><strong>Te va a has&eacute; pupitaa mamaar.'),
            '<p><em><strong>Te va a has&eacute; pupitaa mamaar.</strong></em></p>',
        )
        self.assertEqual(
            html.close_tags('Est&#225; la cosa muy <strong><em>malar</strong>.'),
            'Est&#225; la cosa muy <strong><em>malar</strong>.</em>',
        )

    def test_extract_text(self):
        self.assertEqual(
            html.extract_text('<p><strong>Lorem fistrum</strong> pecador.</p>'),
            'Lorem fistrum pecador.',
        )
        self.assertEqual(
            html.extract_text('<p><em>Te va a has&eacute; pupitaa mamaar.</em></p>'),
            'Te va a hasé pupitaa mamaar.',
        )
        self.assertEqual(
            html.extract_text('Est&#225; la cosa muy <strong><em>malar<strong>.'),
            'Está la cosa muy malar.',
        )


class HtmlEntitiesTest(test.SimpleTestCase):

    def test_decode(self):
        self.assertEqual(htmlentities.decode('&lt;'), '<')
        self.assertEqual(htmlentities.decode('&#60;'), '<')
        self.assertEqual(htmlentities.decode('&euro;'), '€')
        self.assertEqual(htmlentities.decode('&#8364;'), '€')
        self.assertEqual(htmlentities.decode('&#x20AC;'), '€')
        self.assertEqual(htmlentities.decode('&notin;'), '∉')
        self.assertEqual(htmlentities.decode('&#8713;'), '∉')
        self.assertEqual(htmlentities.decode('&Gamma;'), 'Γ')
        self.assertEqual(htmlentities.decode('Γ'), 'Γ')
        self.assertEqual(htmlentities.decode('&spades;'), '♠')
        self.assertEqual(htmlentities.decode('&#9824;'), '♠')
        self.assertEqual(htmlentities.decode('&#2384;'), 'ॐ')
        self.assertEqual(htmlentities.decode('&#x950;'), 'ॐ')

    def test_encode(self):
        self.assertEqual(htmlentities.encode('<'), '&lt;')
        self.assertEqual(htmlentities.encode('€'), '&euro;')
        self.assertEqual(htmlentities.encode('∉'), '&notin;')
        self.assertEqual(htmlentities.encode('Γ'), '&Gamma;')
        self.assertEqual(htmlentities.encode('♠'), '&spades;')
        self.assertEqual(htmlentities.encode('ॐ'), '&#2384;')


class MinifierTest(test.SimpleTestCase):

    css_code = (
        '\n'
        '    your css {  \n'
        '        content: "!" ; \n'
        '    } \n'
        '\n'
    )
    minified_css_code = (
        'your css{content:"!"}\n'
    )
    html_code = (
        '<!DOCTYPE html>\n'
        '<html>\n'
        '  <head>\n'
        '    <title>This is a title</title>\n'
        '    <!--This is a comment.-->\n'
        '    <!--[if IE]>This is a conditional comment<![endif]-->\n'
        '  </head>\n'
        '  <body>\n'
        '\n'
        '    <p>This is a paragraph.</p>\n'
        '    \n'
        '    <!-- This is another comment. -->\n'
        '    <pre>\n'
        '      This a preformatted text.\n'
        '    </pre>\n'
        '\n'
        '  </body>\n'
        '</html>\n'
    )
    minified_html_code = (
        '<!DOCTYPE html>\n'
        '<html>\n'
        '<head>\n'
        '<title>This is a title</title>\n'
        '<!--[if IE]>This is a conditional comment<![endif]-->\n'
        '</head>\n'
        '<body>\n'
        '<p>This is a paragraph.</p>\n'
        '<pre>\n'
        '      This a preformatted text.\n'
        '    </pre>\n'
        '</body>\n'
        '</html>\n'
    )
    js_code = (
        '$( document ).ready(function() {\n'
        ' \n'
        '    $( "a" ).click(function( event ) {\n'
        ' \n'
        '        alert( "Thanks for visiting!" );\n'
        ' \n'
        '    });\n'
        ' \n'
        '});\n'
    )
    minified_js_code = (
        '$( document ).ready(function() {\n'
        '$( "a" ).click(function( event ) {\n'
        'alert( "Thanks for visiting!" );\n'
        '});\n'
        '});\n'
    )
    maxDiff = None

    @minifier_decorators.minify_css_output
    def minifyCss(self, code):
        return code

    @minifier_decorators.minify_html_output
    def minifyHtml(self, code):
        return code

    @minifier_decorators.minify_js_output
    def minifyJs(self, code):
        return code

    def test_minify_css(self):
        self.assertEqual(minifier.minify_css(self.css_code), self.minified_css_code)

    def test_minify_css_output(self):
        self.assertEqual(self.minifyCss(self.css_code), self.minified_css_code)

    def test_minify_html(self):
        self.assertEqual(minifier.minify_html(self.html_code), self.minified_html_code)

    def test_minify_html_output(self):
        self.assertEqual(self.minifyHtml(self.html_code), self.minified_html_code)

    def test_minify_js(self):
        self.assertEqual(minifier.minify_js(self.js_code), self.minified_js_code)

    def test_minify_js_output(self):
        self.assertEqual(self.minifyJs(self.js_code), self.minified_js_code)


class ModulesTest(test.SimpleTestCase):

    def test_valid_module(self):
        module = modules.import_module('cgi')
        import cgi
        self.assertEqual(module, cgi)
        self.assertIs(module, cgi)

    def test_missing_module(self):
        with self.assertRaises(ImportError):
            modules.import_module('asdfg')

        module = modules.import_module(
            'asdfg',
            ignore_missing=True,
        )
        self.assertIsNone(module)

    def test_invalid_dependency(self):
        with self.assertRaises(ImportError):
            modules.import_module('utils.invalid_dependency')

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter('always')
            module = modules.import_module(
                'utils.invalid_dependency',
                ignore_internal_errors=True,
            )
            self.assertEqual(len(w), 1)
            self.assertTrue(issubclass(w[0].category, ImportWarning))
            self.assertIn('No module', str(w[0].message))
            self.assertIsNone(module)

    def test_invalid_syntax(self):
        with self.assertRaises(SyntaxError):
            modules.import_module('utils.invalid_syntax')

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter('always')
            module = modules.import_module(
                'utils.invalid_syntax',
                ignore_internal_errors=True,
            )
            self.assertEqual(len(w), 1)
            self.assertTrue(issubclass(w[0].category, SyntaxWarning))
            self.assertIn('invalid syntax', str(w[0].message))
            self.assertIsNone(module)


class PropertiesTest(test.SimpleTestCase):

    def test_cached_property(self):

        class TestClass(object):
            @properties.cached_property
            def cached_property(self):
                return random.random()

        obj = TestClass()
        first_value = obj.cached_property
        for i in range(10):
            self.assertEqual(obj.cached_property, first_value)

        class TestClass(object):
            def random_method(self):
                return random.random()
            cached_property = properties.cached_property(random_method, 'cached_property')

        obj = TestClass()
        first_value = obj.cached_property
        for i in range(10):
            self.assertEqual(obj.cached_property, first_value)

        previous_values = []
        for i in range(10):
            value = obj.random_method()
            self.assertNotIn(value, previous_values)
            previous_values.append(value)

    def test_class_property(self):

        class TestClass(object):
            @properties.class_property
            def class_property(self):
                return 'Bilbo'

        self.assertEqual(TestClass.class_property, 'Bilbo')
        obj = TestClass()
        with self.assertRaises(AttributeError):
            obj.class_property

    def test_described_property(self):

        class TestClass(object):
            @properties.described_property('First Property')
            def first_property(self):
                return random.random()
            @properties.described_property('Second Property', allow_tags=True, boolean=True, cached=True)
            def second_property(self):
                return random.random()

        obj = TestClass()

        self.assertIsInstance(
            TestClass.first_property,
            property,
        )
        self.assertEqual(
            TestClass.first_property.fget.short_description,
            'First Property'
        )
        self.assertFalse(TestClass.first_property.fget.allow_tags)
        self.assertFalse(TestClass.first_property.fget.boolean)

        first_value = obj.first_property
        for i in range(10):
            self.assertNotEqual(obj.first_property, first_value)

        self.assertIsInstance(
            TestClass.second_property,
            properties.cached_property,
        )
        self.assertEqual(
            TestClass.second_property.fget.short_description,
            'Second Property'
        )
        self.assertTrue(TestClass.second_property.fget.allow_tags)
        self.assertTrue(TestClass.second_property.fget.boolean)

        first_value = obj.second_property
        for i in range(10):
            self.assertEqual(obj.second_property, first_value)


class SlugifyTest(test.SimpleTestCase):

    def checkSlug(self, tests):
        for string, slug in tests:
            self.assertEqual(slugify(string), slug)

    def test_usage(self):
        a = 'Ελληνικά'
        b = '-'.join((a, a))
        c = ' - '.join((a, a))
        self.checkSlug([
            ('xx x  - "#$@ x',
             'xx-x-x'),
            ('Bän...g (bang)',
             'bän-g-bang'),
            (a,
             a.lower()),
            (b,
             b.lower()),
            (c,
             b.lower()),
            ('    a ',
             'a'),
            ('tags/',
             'tags'),
            ('holy_wars',
             'holy-wars'),

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


class UnidecodeTest(test.SimpleTestCase):

    def checkUnidecode(self, tests):
        for unicode, ascii in tests:
            self.assertEqual(unidecode(unicode), ascii)

    def test_ascii(self):
        for n in range(0, 128):
            self.assertEqual(
                unidecode(chr(n)),
                chr(n),
            )

    def test_bmp(self):
        # Just check that it doesn't throw an exception
        for n in range(0, 0x10000):
            unidecode(chr(n))

    def test_circled_latin(self):
        # 1 sequence of a-z
        for n in range(0, 26):
            self.assertEqual(
                unidecode(chr(0x24d0 + n)),
                chr(ord('a') + n),
            )

    @skipIf(sys.maxunicode < 0x10000, 'Narrow build.')
    def test_mathematical_latin(self):
        # 13 consecutive sequences of A-Z, a-z with some codepoints
        # undefined. We just count the undefined ones and don't check
        # positions.
        empty_count = 0
        for n in range(0x1d400, 0x1d6a4):
            a = unidecode(chr(n))
            if n % 52 < 26:
                b = chr(ord('A') + n % 26)
            else:
                b = chr(ord('a') + n % 26)
            if not a:
                empty_count += 1
            else:
                self.assertEqual(a, b)

        self.assertEqual(empty_count, 24)

    @skipIf(sys.maxunicode < 0x10000, 'Narrow build.')
    def test_mathematical_digits(self):
        # 5 consecutive sequences of 0-9
        for n in range(0x1d7ce, 0x1d800):
            self.assertEqual(
                unidecode(chr(n)),
                chr(ord('0') + (n-0x1d7ce) % 10),
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

