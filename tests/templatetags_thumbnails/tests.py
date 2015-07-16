# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from django.test import SimpleTestCase
from django.template import Context, Template

from yepes.templatetags.thumbnails import GetThumbnailTag
from yepes.test_mixins import TemplateTagsMixin


class ThumbnailTagsTest(TemplateTagsMixin, SimpleTestCase):

    required_libraries = ['thumbnails']

    def test_get_thumbnail_syntax(self):
        self.checkSyntax(
            GetThumbnailTag,
            '{% get_thumbnail source config[ as variable_name] %}',
        )

