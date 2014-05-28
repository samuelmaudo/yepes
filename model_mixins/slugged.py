# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from django.db import models
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _

from yepes import fields
from yepes import managers
from yepes.urlresolvers import build_full_url


class Slugged(models.Model):
    """
    Abstract model that handles auto-generating slugs.
    """

    slug = fields.SlugField(
            max_length=63,
            blank=True,
            verbose_name=_('Slug'),
            help_text=_('URL friendly version of the main title. '
                        'It is usually all lowercase and contains only letters, numbers and hyphens.'))

    objects = managers.SluggedManager()

    class Meta:
        abstract = True

    def onsite_link(self):
        link = '<a href="{0}">{1}</a>'
        return link.format(self.get_full_url(), _('View on site'))
    onsite_link.allow_tags = True
    onsite_link.short_description = ''

    def get_full_url(self):
        return build_full_url(self.get_absolute_url())

    def get_link(self):
        return mark_safe('<a href="{0}">{1}</a>'.format(
                         self.get_absolute_url(),
                         self))

    def natural_key(self):
        return (self.slug, )

