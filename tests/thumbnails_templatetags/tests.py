# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from base64 import b64encode
from hashlib import md5
import os

from django.test import TestCase
from django.template import Context, Template
from django.utils.encoding import force_bytes

from yepes.apps.thumbnails.models import Configuration
from yepes.apps.thumbnails.templatetags.thumbnails import (
    GetThumbnailTag,
    MakeThumbnailTag,
)
from yepes.apps.thumbnails.test_mixins import ThumbnailsMixin
from yepes.test_mixins import TemplateTagsMixin


class ThumbnailTagsTest(ThumbnailsMixin, TemplateTagsMixin, TestCase):

    requiredLibraries = ['thumbnails']
    tempDirPrefix = 'test_thumbnails_templatetags_'

    def setUp(self):
        super(ThumbnailTagsTest, self).setUp()
        Configuration.objects.create(
            key='default',
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

    def test_make_thumbnail_syntax(self):
        self.checkSyntax(
            MakeThumbnailTag,
            '{% make_thumbnail source width height'
            '[ background[ mode[ algorithm[ gravity[ format[ quality]]]]]]'
            '[ as variable_name] %}',
        )

    def test_make_thumbnail(self):
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
            {% make_thumbnail source 100 50 %}
            {{ thumbnail.path }}
        ''')
        self.assertEqual(template.render(context).strip(), path)

    def test_render_image_tag(self):
        self.source.generate_thumbnail('default')
        thumbnail = self.source.get_existing_thumbnail('default')
        self.assertTrue(thumbnail.closed)

        context = Context({'thumbnail': thumbnail})
        template = Template('{{ thumbnail.get_tag }}')
        tag = template.render(context)
        self.assertTrue(thumbnail.closed)

        self.assertTrue(tag.startswith('<img '))
        self.assertTrue(tag.endswith('">'))
        self.assertEqual(set(tag[1:-1].split()), {
            'img',
            'src="{0}"'.format(thumbnail.url),
            'width="{0}"'.format(thumbnail.width),
            'height="{0}"'.format(thumbnail.height),
        })
        self.assertTrue(thumbnail.closed)

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


