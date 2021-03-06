# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from django.core.exceptions import ImproperlyConfigured
from django.utils import six
from django.utils.encoding import force_text
from django.utils.functional import Promise
from django.utils.itercompat import is_iterable

from yepes.contrib.sitemaps import StaticSitemap
from yepes.views import CachedTemplateView


class SitemapView(CachedTemplateView):

    content_type = 'application/xml'
    sitemap_class = None
    template_name = 'sitemap.xml'
    timeout = 86400

    def get_context_data(self, **context):
        sitemap_class = self.get_sitemap_class()
        sitemap = self.get_sitemap(sitemap_class)
        context['urlset'] = sitemap.get_urls()
        return context

    def get_sitemap(self, sitemap_class):
        return sitemap_class(**self.get_sitemap_kwargs())

    def get_sitemap_class(self):
        if not self.sitemap_class:
            msg = ('{cls} is missing a sitemap.'
                   ' Define {cls}.sitemap_class'
                   ' or override {cls}.get_sitemap_class().')
            raise ImproperlyConfigured(msg.format(cls=self.__class__.__name__))

        return self.sitemap_class

    def get_sitemap_kwargs(self):
        return {}


class StaticSitemapView(SitemapView):

    sitemap_class = StaticSitemap
    url_names = None

    def get_sitemap_kwargs(self):
        if not self.url_names:
            msg = ('{cls} is missing url names.'
                   ' Define {cls}.url_names'
                   ' or override {cls}.get_sitemap_kwargs().')
            raise ImproperlyConfigured(msg.format(cls=self.__class__.__name__))

        kwargs = super(StaticSitemapView, self).get_sitemap_kwargs()
        kwargs['url_names'] = self.url_names
        return kwargs


class SitemapIndexView(CachedTemplateView):

    content_type = 'application/xml'
    sitemap_urls = None
    template_name = 'sitemap_index.xml'
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

