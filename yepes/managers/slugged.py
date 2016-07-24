# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from django.db.models import Manager

from yepes.apps import apps


class SluggedManager(Manager):
    """
    Provides access to items using their natural key: the ``slug`` field.
    """
    def get_by_natural_key(self, slug):
        return self.get(slug=slug)

    def get_by_slug(self, slug, pk=None):
        """
        Returns the object with the given ``slug``.

        If ``yepes.contrib.slugs`` is installed, it searches through the
        entire slug history. Otherwise, it only searches through the current
        slugs.

        """
        if 'slugs' in apps:
            qs = self.get_queryset()
            qs = qs.order_by('-slug_history__id')
            qs = qs.filter(slug_history__slug=slug)
            if pk is not None:
                qs = qs.filter(slug_history__object_id=pk)

            return qs[:1].get()
        else:
            return self.get(slug=slug)

