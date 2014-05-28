# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from django.core.exceptions import ImproperlyConfigured
from django.utils import six
from django.utils.encoding import force_text
from django.utils.functional import Promise
from django.utils.itercompat import is_iterable

from yepes.views import CachedTemplateView


class SitemapView(CachedTemplateView):

    content_type = 'application/xml'
    sitemap = None
    timeout = 86400

    def get_context_data(self, **context):
        context['urlset'] = self.get_sitemap(**self.kwargs).get_urls()
        return context

    def get_sitemap(self, **kwargs):
        if not self.sitemap:
            msg = ('{cls} is missing a sitemap.'
                   ' Define {cls}.sitemap or override {cls}.get_sitemap().')
            raise ImproperlyConfigured(msg.format(cls=self.__class__.__name__))

        return self.sitemap(**kwargs)

    def get_template_names(self):
        templates = []
        if isinstance(self.template_name, six.string_types):
            templates.append(self.template_name)
        elif is_iterable(self.template_name):
            templates.extend(self.template_name)

        templates.append('sitemap.xml')
        return templates

    def get_use_cache(self, request):
        return (not request.user.is_staff)


class SitemapIndexView(CachedTemplateView):

    content_type = 'application/xml'
    sitemap_urls = None
    timeout = 86400

    def get_context_data(self, **context):
        context['sitemaps'] = self.get_sitemap_urls()
        return context

    def get_sitemap_urls(self):
        if not self.sitemap_urls:
            msg = ('No sitemap url was provided.'
                   ' Define {cls}.sitemap_urls'
                   ' or override {cls}.get_sitemap_urls().')
            raise ImproperlyConfigured(msg.format(cls=self.__class__.__name__))

        urls = []
        for url in self.sitemap_urls:
            if isinstance(url, six.string_types):
                urls.append(url)
            elif isinstance(url, Promise):
                urls.append(force_text(url))
            elif is_iterable(url):
                urls.extend(url)

        return urls

    def get_template_names(self):
        templates = []
        if isinstance(self.template_name, six.string_types):
            templates.append(self.template_name)
        elif is_iterable(self.template_name):
            templates.extend(self.template_name)

        templates.append('sitemap_index.xml')
        return templates

    def get_use_cache(self, request):
        return (not request.user.is_staff)

