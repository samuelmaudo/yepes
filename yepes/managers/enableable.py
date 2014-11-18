# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from django.db.models import Manager
from django.db.models.query import QuerySet


class EnableableQuerySet(QuerySet):
    """
    QuerySet providing main search functionality for ``EnableableManager``.
    """

    def disabled(self, user=None):
        """
        Returns disabled items.
        """
        return self.filter(is_enabled=False)

    def enabled(self, user=None):
        """
        Returns enabled items.
        """
        if user is not None and user.is_staff:
            return self.all()
        return self.filter(is_enabled=True)


class EnableableManager(Manager):
    """
    Provides filter for restricting items returned by ``is_enabled``.
    """

    def get_queryset(self):
        return EnableableQuerySet(self.model, using=self._db)

    def disabled(self, *args, **kwargs):
        """
        Returns disabled items.
        """
        return self.get_queryset().disabled(*args, **kwargs)

    def enabled(self, *args, **kwargs):
        """
        Returns enabled items.
        """
        return self.get_queryset().enabled(*args, **kwargs)

