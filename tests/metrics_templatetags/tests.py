# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from django.test import SimpleTestCase
from django.template import Context, Template

from yepes.templatetags.metrics import AnalyticsScriptTag
from yepes.test_mixins import TemplateTagsMixin


class MetricTagsTest(TemplateTagsMixin, SimpleTestCase):

    requiredLibraries = ['metrics']

    def test_analytics_script_syntax(self):
        self.checkSyntax(
            AnalyticsScriptTag,
            '{% analytics_script[ site_id[ cookie_domain[ cookie_age[ cookie_name[ cookie_path[ use_cookies[ template]]]]]]] %}',
        )

