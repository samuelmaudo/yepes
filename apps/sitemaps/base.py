# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from django.contrib.sitemaps import Sitemap
from django.core.urlresolvers import reverse
from django.utils import six

from yepes.urlresolvers import full_reverse


class FullUrlSitemap(Sitemap):
    """
    Uses full qualified URLs instead of using root relative URLs.
    """
    homogeneous = True
    paginate = False
    _prefix = None

    def get_urls(self, page=1, *args, **kwargs):

        if self.paginate:
            items = self.paginator.page(page).object_list
        elif page == 1:
            items = self.items()
        else:
            items = ()

        urls = [
            {
                'item': i,
                'location': self._Sitemap__get('location', i),
                'lastmod': self._Sitemap__get('lastmod', i, None),
                'changefreq': self._Sitemap__get('changefreq', i, None),
                'priority': six.text_type(self._Sitemap__get('priority', i, None) or ''),
            }
            for i
            in items
        ]
        return urls

    def location(self, obj):
        """
        Try to obtain the item location by calling ``obj.get_full_url()``.
        """
        if not self.homogeneous:
            return obj.get_full_url()

        if self._prefix is None:
            full_url = obj.get_full_url()
            absolute_url = obj.get_absolute_url()
            common = full_url[0:-len(absolute_url)]
            if common + absolute_url != full_url:
                self.homogeneous = False
                return full_url
            else:
                self._prefix = common + '{0}'
                return full_url

        return self._prefix.format(obj.get_absolute_url())


class StaticSitemap(FullUrlSitemap):
    """
    Return the static sitemap items.
    """
    changefreq = 'never'
    homogeneous = False
    priority = 0.3

    def __init__(self, url_names, priority=None, changefreq=None):
        self.url_names = url_names
        if priority is not None:
            self.priority = priority
        if changefreq is not None:
            self.changefreq = changefreq

    def items(self):
        return tuple(self.url_names)

    def location(self, obj):
        if not self.homogeneous:
            return full_reverse(obj)

        if self._prefix is None:
            full_url = full_reverse(obj)
            absolute_url = reverse(obj)
            common = full_url[0:-len(absolute_url)]
            if common + absolute_url != full_url:
                self.homogeneous = False
                return full_url
            else:
                self._prefix = common + '{0}'
                return full_url

        return self._prefix.format(reverse(obj))

