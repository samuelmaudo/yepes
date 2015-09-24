# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from django.test import SimpleTestCase
from django.template import Context, Template

from yepes.defaulttags import (
    BuildFullUrlTag,
    CacheTag,
    FullUrlTag,
    PaginationTag,
    PhasedTag,
)
from yepes.test_mixins import TemplateTagsMixin


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

