# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from django.db import models
from django.utils import six
from django.utils.html import format_html
from django.utils.translation import ugettext as _

from yepes.urlresolvers import build_full_url
from yepes.utils.html import make_double_tag


class Linked(models.Model):
    """
    Abstract model that adds support for full urls. It also adds two helper
    methods to easily get object links.
    """

    class Meta:
        abstract = True

    def get_full_url(self):
        return build_full_url(self.get_absolute_url())

    def get_link(self, **attrs):
        attrs['href'] = self.get_absolute_url()

        text = self.get_link_text()
        if not text:
            text = attrs['href']

        return make_double_tag('a', text, attrs)

    def get_link_text(self):
        return six.text_type(self)

    def onsite_link(self):
        url = self.get_full_url()
        text = _('View on site')
        return format_html('<a href="{0}">{1}</a>', url, text)
    onsite_link.allow_tags = True
    onsite_link.short_description = ''

