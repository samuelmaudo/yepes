# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from django.db import models
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _

from yepes.urlresolvers import build_full_url


class Linked(models.Model):
    """
    Abstract model that adds support for full urls. It also adds two helper
    methods to easily get object links.
    """

    class Meta:
        abstract = True

    def get_full_url(self):
        return build_full_url(self.get_absolute_url())

    def get_link(self):
        return mark_safe('<a href="{0}">{1}</a>'.format(
                         self.get_absolute_url(),
                         self))

    def onsite_link(self):
        return '<a href="{0}">{1}</a>'.format(
                self.get_full_url(),
                _('View on site'))
    onsite_link.allow_tags = True
    onsite_link.short_description = ''

