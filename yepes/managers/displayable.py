# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from .publishable import PublishableManager, PublishableQuerySet
from .searchable import SearchableManager, SearchableQuerySet
from .slugged import SluggedManager


class DisplayableQuerySet(PublishableQuerySet, SearchableQuerySet):
    """
    QuerySet providing main search functionality for ``PublishableManager``.
    """
    pass


class DisplayableManager(PublishableManager, SearchableManager, SluggedManager):
    """
    Manually combines ``PublishableManager``, ``SearchableManager`` and
    ``SluggedManager`` for the ``Displayable`` model.
    """
    def get_queryset(self):
        kwargs = {
            'search_fields': self.get_search_fields(),
            'using': self._db,
        }
        return DisplayableQuerySet(self.model, **kwargs)

