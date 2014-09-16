# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from django.db.models import Manager, Q
from django.db.models.query import QuerySet
from django.utils import timezone


class PublishableQuerySet(QuerySet):
    """
    QuerySet providing main search functionality for ``PublishableManager``.
    """

    def published(self, user=None, date=None):
        """
        Returns items with a published status and whose publication dates fall
        before and after the current date when specified.
        """
        from yepes.model_mixins import Displayable
        if user is not None and user.is_staff:
            return self.all()
        if not date:
            date = timezone.now()
        return self.filter(
            Q(publish_status=Displayable.PUBLISHED),
            Q(publish_from=None) | Q(publish_from__lte=date),
            Q(publish_to=None) | Q(publish_to__gte=date))

    def unpublished(self, user=None, date=None):
        """
        Returns items with published status but whose publication dates don't
        cover the current date.
        """
        from yepes.model_mixins import Displayable
        if not date:
            date = timezone.now()
        return self.filter(
            Q(publish_status=Displayable.PUBLISHED),
            Q(publish_from__gt=date) | Q(publish_to__lt=date))


class PublishableManager(Manager):
    """
    Provides filter for restricting items returned by ``publish_status``,
    ``publish_from`` and `publish_to`.
    """

    def get_queryset(self):
        return PublishableQuerySet(self.model, using=self._db)

    def published(self, *args, **kwargs):
        """
        Returns items with published status and whose publication dates fall
        before and after the current date when specified.
        """
        return self.get_queryset().published(*args, **kwargs)

    def unpublished(self, *args, **kwargs):
        """
        Returns items with published status but whose publication dates don't
        cover the current date.
        """
        return self.get_queryset().unpublished(*args, **kwargs)

