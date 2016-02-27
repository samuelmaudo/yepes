# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from django.test import SimpleTestCase, TestCase
from django.test.utils import override_settings
from django.template import Context, Template, TemplateSyntaxError

from yepes.defaulttags import (
    BuildFullUrlTag,
    CacheTag,
    FullUrlTag,
    PaginationTag,
    PhasedTag,
)
from yepes.templatetags.svg import (
    InsertFileTag,
    InsertSymbolTag,
)
from yepes.templatetags.trees import (
    RecurseTag,
)
from yepes.test_mixins import TemplateTagsMixin

from .models import Category


class DefaultTagsTest(TemplateTagsMixin, SimpleTestCase):

    def test_build_full_url_syntax(self):
        self.checkSyntax(
            BuildFullUrlTag,
            '{% build_full_url location **kwargs[ as variable_name] %}',
        )

    def test_cache_syntax(self):
        self.checkSyntax(
            CacheTag,
            '{% cache expire_time fragment_name *vary_on %}...{% endcache %}',
        )

    def test_full_url_syntax(self):
        self.checkSyntax(
            FullUrlTag,
            '{% full_url view_name *args **kwargs[ as variable_name] %}',
        )

    def test_pagination_syntax(self):
        self.checkSyntax(
            PaginationTag,
            '{% pagination[ paginator[ page_obj]] **kwargs %}',
        )

    def test_phased_syntax(self):
        self.checkSyntax(
            PhasedTag,
            '{% phased[ with *vars **new_vars] %}...{% endphased %}',
        )


class SvgTagsTest(TemplateTagsMixin, SimpleTestCase):

    requiredLibraries = ['svg']

    def test_insert_file_syntax(self):
        self.checkSyntax(
            InsertFileTag,
            '{% insert_file file_name[ method] %}',
        )

    @override_settings(DEBUG=True)
    def test_insert_file(self):
        template = Template('''
            {% load svg %}
            {% insert_file 'invalid-file' %}
        ''')
        context = Context()
        html = template.render(context)

        self.assertEqual(html.strip(), '')

        template = Template('''
            {% load svg %}
            {% insert_file 'svg/icon.svg' %}
        ''')
        context = Context()
        html = template.render(context)

        self.assertHTMLEqual(html, '''
            <svg width="16" height="16">
                <rect style="fill:#4d4d4d" width="6" height="6" x="5" y="5"/>
            </svg>
        ''')

        template = Template('''
            {% load svg %}
            {% insert_file 'svg/icon.svg' method='img' %}
        ''')
        context = Context()
        html = template.render(context)

        self.assertHTMLEqual(html, '''
            <img src="data:image/svg+xml;charset=utf8,%3Csvg xmlns='http://www.w3.org/2000/svg'%3E%3Crect style='fill:%234d4d4d' width='6' height='6' x='5' y='5'/%3E%3C/svg%3E" width="16" height="16" />
        ''')

        template = Template('''
            {% load svg %}
            {% insert_file 'svg/icon.svg' 'invalid-method' %}
        ''')
        context = Context()
        with self.assertRaises(TemplateSyntaxError):
            template.render(context)


    def test_insert_symbol_syntax(self):
        self.checkSyntax(
            InsertSymbolTag,
            '{% insert_symbol file_name symbol_name[ method] %}',
        )

    @override_settings(DEBUG=True)
    def test_insert_symbol(self):
        template = Template('''
            {% load svg %}
            {% insert_symbol 'invalid-file' 'invalid-symbol' %}
        ''')
        context = Context()
        html = template.render(context)

        self.assertEqual(html.strip(), '')

        template = Template('''
            {% load svg %}
            {% insert_symbol 'svg/iconvault.svg' 'invalid-symbol' %}
        ''')
        context = Context()
        html = template.render(context)

        self.assertEqual(html.strip(), '')

        template = Template('''
            {% load svg %}
            {% insert_symbol 'svg/iconvault.svg' 'media-playback-stop' %}
        ''')
        context = Context()
        html = template.render(context)

        self.assertHTMLEqual(html, '''
            <svg width="16" height="16">
                <rect style="fill:#4d4d4d" width="6" height="6" x="5" y="5"/>
            </svg>
        ''')

        template = Template('''
            {% load svg %}
            {% insert_symbol 'svg/iconvault.svg' 'media-playback-stop' method='img' %}
        ''')
        context = Context()
        html = template.render(context)

        self.assertHTMLEqual(html, '''
            <img src="data:image/svg+xml;charset=utf8,%3Csvg xmlns='http://www.w3.org/2000/svg'%3E%3Crect style='fill:%234d4d4d' width='6' height='6' x='5' y='5'/%3E%3C/svg%3E" width="16" height="16" />
        ''')

        template = Template('''
            {% load svg %}
            {% insert_symbol 'svg/iconvault.svg' 'media-playback-stop' 'invalid-method' %}
        ''')
        context = Context()
        with self.assertRaises(TemplateSyntaxError):
            template.render(context)


class TreesTagsTest(TemplateTagsMixin, TestCase):

    requiredLibraries = ['trees']

    def setUp(self):
        def factory(n, p=None):
            return Category.objects.create(name=n, parent=p)

        root = factory('PC & Video Games')
        wii = factory('Nintendo Wii', root)
        wii_games = factory('Games', wii)
        wii_hardware = factory('Hardware & Accessories', wii)
        xbox = factory('Xbox 360', root)
        xbox_games = factory('Games', xbox)
        xbox_hardware = factory('Hardware & Accessories', xbox)
        play = factory('PlayStation 3', root)
        play_games = factory('Games', play)
        play_hardware = factory('Hardware & Accessories', play)

        def getter(n, p=None):
            return Category.objects.get(name=n, parent=p)

        self.root = getter('PC & Video Games')
        self.wii = getter('Nintendo Wii', root)
        self.wii_games = getter('Games', wii)
        self.wii_hardware = getter('Hardware & Accessories', wii)
        self.xbox = getter('Xbox 360', root)
        self.xbox_games = getter('Games', xbox)
        self.xbox_hardware = getter('Hardware & Accessories', xbox)
        self.play = getter('PlayStation 3', root)
        self.play_games = getter('Games', play)
        self.play_hardware = getter('Hardware & Accessories', play)

    def test_recurse_syntax(self):
        self.checkSyntax(
            RecurseTag,
            '{% recurse tree %}...{% endrecurse %}',
        )

    def test_recurse(self):
        template = Template('''
            {% load trees %}
            <ul>
              {% recurse tree %}
                <li>
                  {{ node.name }}
                  {% if not node.is_leaf_node %}
                    <ul class="children">
                      {{ children }}
                    </ul>
                  {% endif %}
                </li>
              {% endrecurse %}
            </ul>
        ''')
        # TREE NODE
        context = Context({
            'tree': self.root,
        })
        with self.assertNumQueries(1):
            html = template.render(context)

        self.assertHTMLEqual(html,'''
            <ul>
              <li>
                Nintendo Wii
                <ul class="children">
                  <li>Games</li>
                  <li>Hardware &amp; Accessories</li>
                </ul>
              </li>
              <li>
                PlayStation 3
                <ul class="children">
                  <li>Games</li>
                  <li>Hardware &amp; Accessories</li>
                </ul>
              </li>
              <li>
                Xbox 360
                <ul class="children">
                  <li>Games</li>
                  <li>Hardware &amp; Accessories</li>
                </ul>
              </li>
            </ul>
        ''')
        # NODE LIST
        context = Context({
            'tree': [self.wii, self.xbox],
        })
        with self.assertNumQueries(2):
            html = template.render(context)

        self.assertHTMLEqual(html,'''
            <ul>
              <li>
                Nintendo Wii
                <ul class="children">
                  <li>Games</li>
                  <li>Hardware &amp; Accessories</li>
                </ul>
              </li>
              <li>
                Xbox 360
                <ul class="children">
                  <li>Games</li>
                  <li>Hardware &amp; Accessories</li>
                </ul>
              </li>
            </ul>
        ''')
        # NODE QUERYSET
        context = Context({
            'tree': Category.objects.trees(),
        })
        with self.assertNumQueries(1):
            html = template.render(context)

        self.assertHTMLEqual(html,'''
            <ul>
              <li>
                PC &amp; Video Games
                <ul class="children">
                  <li>
                    Nintendo Wii
                    <ul class="children">
                      <li>Games</li>
                      <li>Hardware &amp; Accessories</li>
                    </ul>
                  </li>
                  <li>
                    PlayStation 3
                    <ul class="children">
                      <li>Games</li>
                      <li>Hardware &amp; Accessories</li>
                    </ul>
                  </li>
                  <li>
                    Xbox 360
                    <ul class="children">
                      <li>Games</li>
                      <li>Hardware &amp; Accessories</li>
                    </ul>
                  </li>
                </ul>
              </li>
            </ul>
        ''')

