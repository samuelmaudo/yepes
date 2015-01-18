# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _

from yepes import fields
from yepes import managers
from yepes.model_mixins import Linked


class Slugged(Linked):
    """
    Abstract model that handles auto-generating slugs. Inherits from `Linked`.
    """

    slug = fields.SlugField(
            max_length=63,
            unique=True,
            verbose_name=_('Slug'),
            help_text=_('URL friendly version of the main title. '
                        'It is usually all lowercase and contains only letters, numbers and hyphens.'))

    objects = managers.SluggedManager()

    class Meta:
        abstract = True

    def natural_key(self):
        return (self.slug, )

