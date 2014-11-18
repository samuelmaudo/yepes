# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from django.db.models import Manager


class SluggedManager(Manager):
    """
    Provides access to items using their natural key: the ``slug`` field.
    """
    def get_by_natural_key(self, slug):
        return self.get(slug=slug)

