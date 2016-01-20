# -*- coding:utf-8 -*-

from yepes.managers.activatable import ActivatableManager, ActivatableQuerySet
from yepes.managers.displayable import DisplayableManager, DisplayableQuerySet
from yepes.managers.enableable import EnableableManager, EnableableQuerySet
from yepes.managers.publishable import PublishableManager, PublishableQuerySet
from yepes.managers.searchable import SearchableManager, SearchableQuerySet
from yepes.managers.slugged import SluggedManager

try:
    import mptt
except ImportError:
    pass
else:
    from yepes.managers.nestable import (
        NestableManager,
        NestableQuerySet,
        TreeQuerySet,
    )
