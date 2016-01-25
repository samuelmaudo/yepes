# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from base64 import b64encode
from hashlib import md5
import os

from django.test import TestCase
from django.template import Context, Template
from django.utils.encoding import force_bytes

from yepes.apps.thumbnails.models import Configuration
from yepes.apps.thumbnails.proxies import ConfigurationProxy
from yepes.apps.thumbnails.templatetags.thumbnails import (
    GetThumbnailTag,
    MakeConfigurationTag,
    ThumbnailTagTag,
    ThumbnailUrlTag,
)
from yepes.apps.thumbnails.test_mixins import ThumbnailsMixin
from yepes.test_mixins import TemplateTagsMixin


class ThumbnailTagsTest(ThumbnailsMixin, TemplateTagsMixin, TestCase):

    requiredLibraries = ['thumbnails']
    tempDirPrefix = 'test_thumbnails_templatetags_'

    def setUp(self):
        super(ThumbnailTagsTest, self).setUp()
        self.configuration = Configuration.objects.create(
            key='default',
            width=100,
            height=50,
        )
        self.configuration_proxy = ConfigurationProxy(
            width=100,
            height=50,
        )

    def test_get_thumbnail_syntax(self):
        self.checkSyntax(
            GetThumbnailTag,
            '{% get_thumbnail source config[ as variable_name] %}',
        )

    def test_get_thumbnail(self):
        key = md5(b'default/wolf.jpg').digest()
        key = b64encode(key, b'ab').decode('ascii')[:6]
        path = os.path.join(
            self.temp_dir,
            'thumbs',
            'wolf_{0}.jpg'.format(key),
        )
        context = Context({
            'source': self.source
        })
        template = Template('''
            {% load thumbnails %}
            {% get_thumbnail source 'default' %}
            {{ thumbnail.path }}
        ''')
        self.assertEqual(template.render(context).strip(), path)

    def test_make_configuration_syntax(self):
        self.checkSyntax(
            MakeConfigurationTag,
            '{% make_configuration width height'
            '[ background[ mode[ algorithm[ gravity[ format[ quality]]]]]]'
            '[ as variable_name] %}',
        )

    def test_make_configuration(self):
        context = Context({
            'source': self.source
        })
        key = md5(b'w100_h50/wolf.jpg').digest()
        key = b64encode(key, b'ab').decode('ascii')[:6]
        path = os.path.join(
            self.temp_dir,
            'thumbs',
            'wolf_{0}.jpg'.format(key),
        )
        template = Template('''
            {% load thumbnails %}
            {% make_configuration 100 50 %}
            {% get_thumbnail source configuration %}
            {{ thumbnail.path }}
        ''')
        self.assertEqual(template.render(context).strip(), path)

    def test_thumbnail_tag_syntax(self):
        self.checkSyntax(
            ThumbnailTagTag,
            '{% thumbnail_tag source config **attrs %}',
        )

    def test_thumbnail_tag(self):
        thumbnail = self.source.generate_thumbnail(self.configuration)
        self.source.close()
        self.assertTrue(self.source.closed)

        context = Context({
            'source': self.source,
            'configuration': self.configuration,
        })
        template = Template('''
            {% load thumbnails %}
            {% thumbnail_tag source configuration %}
        ''')
        tag = template.render(context).strip()
        self.assertTrue(self.source.closed)

        self.assertTrue(tag.startswith('<img '))
        self.assertTrue(tag.endswith('">'))
        self.assertEqual(set(tag[1:-1].split()), {
            'img',
            'src="{0}"'.format(thumbnail.url),
            'width="{0}"'.format(thumbnail.width),
            'height="{0}"'.format(thumbnail.height),
        })
        self.assertTrue(self.source.closed)

    def test_thumbnail_url_syntax(self):
        self.checkSyntax(
            ThumbnailUrlTag,
            '{% thumbnail_url source config %}',
        )

    def test_thumbnail_url(self):
        thumbnail = self.source.generate_thumbnail(self.configuration)
        self.source.close()
        self.assertTrue(self.source.closed)

        context = Context({
            'source': self.source,
            'configuration': self.configuration,
        })
        template = Template('''
            {% load thumbnails %}
            {% thumbnail_url source configuration %}
        ''')
        url = template.render(context).strip()
        self.assertTrue(self.source.closed)

        self.assertEqual(url, thumbnail.url)
        self.assertTrue(self.source.closed)

    def test_closing_of_previous_thumbnail(self):
        thumbnail = self.source.generate_thumbnail('default')
        thumbnail.open()
        context = Context({
            'source': self.source,
            'thumbnail': thumbnail,
        })
        template = Template('''
            {% load thumbnails %}
            {% get_thumbnail source 'default' %}
        ''')
        self.assertFalse(thumbnail.closed)
        template.render(context)
        # Generated thumbnails internally use ContentFile and its instances
        # cannot be closed. However, the Image instance is correctly closed.
        self.assertFalse(thumbnail.closed)

        thumbnail = self.source.get_existing_thumbnail('default')
        thumbnail.open()
        context = Context({
            'source': self.source,
            'thumbnail': thumbnail,
        })
        template = Template('''
            {% load thumbnails %}
            {% get_thumbnail source 'default' %}
        ''')
        self.assertFalse(thumbnail.closed)
        template.render(context)
        self.assertTrue(thumbnail.closed)


