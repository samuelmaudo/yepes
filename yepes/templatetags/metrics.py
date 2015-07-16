# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from django.template.base import Library
from django.template.context import Context

from yepes.template import InclusionTag

register = Library()


## {% analytics_script[ site_id[ cookie_domain[ cookie_age[ cookie_name[ cookie_path[ use_cookies[ template]]]]]]] %} #####


class AnalyticsScriptTag(InclusionTag):

    template = 'partials/google_analytics.html'

    def process(self, site_id=None, cookie_domain=None, cookie_age=None,
                      cookie_name=None, cookie_path=None, use_cookies=True,
                      template=None):
        request = self.context.get('request')
        if not request:
            return ''

        new_context = Context(
            autoescape=self.context.autoescape,
            current_app=self.context.current_app,
            use_l10n=self.context.use_l10n,
            use_tz=self.context.use_tz)
        new_context.update({
            'site_id': site_id or request.metrics.site_id,
            'cookie_age': cookie_age,
            'cookie_domain': cookie_domain,
            'cookie_name': cookie_name,
            'cookie_path': cookie_path,
            'use_cookies': use_cookies,
            'visitor_id': request.metrics.visitor_id,
        })
        return self.get_content(new_context)

register.tag('analytics_script', AnalyticsScriptTag.as_tag())

