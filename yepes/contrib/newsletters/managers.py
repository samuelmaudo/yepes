# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from django.db.models import Manager
from django.db.models.query import QuerySet


class NewsletterQuerySet(QuerySet):

    def hidden(self):
        """
        Returns not published newsletters.
        """
        return self.filter(is_published=False)

    def published(self):
        """
        Returns published newsletters.
        """
        return self.filter(is_published=True)


class NewsletterManager(Manager):

    def get_queryset(self):
        return NewsletterQuerySet(self.model, using=self._db)

    def hidden(self, *args, **kwargs):
        """
        Returns not published newsletters.
        """
        return self.get_queryset().hidden(*args, **kwargs)

    def published(self, *args, **kwargs):
        """
        Returns published newsletters.
        """
        return self.get_queryset().published(*args, **kwargs)

