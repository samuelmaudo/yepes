# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from django.db.models import Manager, Q
from django.db.models.query import QuerySet
from django.utils import timezone


class ActivatableQuerySet(QuerySet):
    """
    QuerySet providing main search functionality for ``ActivatableManager``.
    """

    def active(self, user=None, date=None):
        """
        Returns active items whose activation dates fall before and after the
        current date when specified.
        """
        if user is not None and user.is_staff:
            return self.all()
        if not date:
            date = timezone.now()
        return self.filter(
            Q(active_status=True),
            Q(active_from=None) | Q(active_from__lte=date),
            Q(active_to=None) | Q(active_to__gte=date))

    def inactive(self, user=None, date=None):
        """
        Returns inactive items or active items whose activation dates don't
        cover the current date.
        """
        if not date:
            date = timezone.now()
        return self.filter(
            Q(active_status=False)
            | Q(active_from__gt=date)
            | Q(active_to__lt=date))


class ActivatableManager(Manager):
    """
    Provides filter for restricting items returned by ``active_status``,
    ``active_from`` and ``active_to``.
    """

    def get_queryset(self):
        return ActivatableQuerySet(self.model, using=self._db)

    def active(self, *args, **kwargs):
        """
        Returns active items whose activation dates fall before and after the
        current date when specified.
        """
        return self.get_queryset().active(*args, **kwargs)

    def inactive(self, *args, **kwargs):
        """
        Returns inactive items or active items whose activation dates don't
        cover the current date.
        """
        return self.get_queryset().inactive(*args, **kwargs)

