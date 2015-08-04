# -*- coding:utf-8 -*-

from __future__ import unicode_literals

import hashlib
import os

from django.test import TestCase
from django.template import Context, Template

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

    def test_get_thumbnail_syntax(self):
        self.checkSyntax(
            GetThumbnailTag,
            '{% get_thumbnail source config[ as variable_name] %}',
        )

    def test_make_thumbnail_syntax(self):
        self.checkSyntax(
            MakeThumbnailTag,
            '{% make_thumbnail source width height'
            '[ filter[ blur[ format[ quality]]]]'
            '[ as variable_name] %}',
        )

    def test_get_thumbnail(self):
        Configuration.objects.create(
            key='default',
            width=100,
            height=50,
        )
        salt = os.path.join('default', self.source.name)
        salt = hashlib.md5(salt).hexdigest()[:6]
        path = os.path.join(
            self.temp_dir,
            'thumbs',
            'wolf_{0}.jpg'.format(salt),
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

    def test_make_thumbnail(self):
        context = Context({
            'source': self.source
        })
        salt = os.path.join('w100_h50', self.source.name)
        salt = hashlib.md5(salt).hexdigest()[:6]
        path = os.path.join(
            self.temp_dir,
            'thumbs',
            'wolf_{0}.jpg'.format(salt),
        )
        template = Template('''
            {% load thumbnails %}
            {% make_thumbnail source 100 50 %}
            {{ thumbnail.path }}
        ''')
        self.assertEqual(template.render(context).strip(), path)

