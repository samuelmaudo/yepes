# -*- coding:utf-8 -*-

from __future__ import unicode_literals

import os
import tempfile

from django.core.files.storage import FileSystemStorage
from django.test import SimpleTestCase
from django.template import Context, Template
from django.utils import six
from django.utils._os import upath

from yepes.apps.thumbnails.files import ImageFile, SourceFile
from yepes.apps.thumbnails.models import Configuration
from yepes.templatetags.thumbnails import GetThumbnailTag, MakeThumbnailTag
from yepes.test_mixins import TempDirMixin, TemplateTagsMixin


class ThumbnailTagsTest(TempDirMixin, TemplateTagsMixin, SimpleTestCase):

    requiredLibraries = ['thumbnails']
    tempDirPrefix = 'test_templatetags_'

    def setUp(self):
        super(ThumbnailTagsTest, self).setUp()
        self.temp_storage = FileSystemStorage(self.temp_dir)
        self.source_path = os.path.join(
            os.path.dirname(upath(__file__)),
            'static',
            'wolf.jpg',
        )
        self.source_image = ImageFile(open(self.source_path, 'rb'))
        self.source = SourceFile(self.source_image, 'static/wolf.jpg',
                                 storage=self.temp_storage)

    def tearDown(self):
        super(ThumbnailTagsTest, self).tearDown()
        self.source.close()

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
        context = Context({
            'source': self.source
        })
        template = Template('''
            {% load thumbnails %}
            {% get_thumbnail source 'default' %}
            {{ thumbnail.path }}
        ''')
        thumbnail_path = template.render(context).strip()
        self.assertEqual(thumbnail_path, os.path.join(
            self.temp_dir,
            'static',
            'thumbs',
            'wolf.jpg.default.jpg',
        ))

    def test_make_thumbnail(self):
        context = Context({
            'source': self.source
        })
        template = Template('''
            {% load thumbnails %}
            {% make_thumbnail source 100 50 %}
            {{ thumbnail.path }}
        ''')
        thumbnail_path = template.render(context).strip()
        self.assertEqual(thumbnail_path, os.path.join(
            self.temp_dir,
            'static',
            'thumbs',
            'wolf.jpg.w100_h50.jpg',
        ))

