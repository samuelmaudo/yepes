# -*- coding:utf-8 -*-

try:
    from mptt.managers import TreeManager as NestableManager
except ImportError:
    pass

from .activatable import ActivatableManager, ActivatableQuerySet
from .displayable import DisplayableManager, DisplayableQuerySet
from .enableable import EnableableManager, EnableableQuerySet
from .publishable import PublishableManager, PublishableQuerySet
from .searchable import SearchableManager, SearchableQuerySet
from .slugged import SluggedManager
