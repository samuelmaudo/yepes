# -*- coding:utf-8 -*-

from yepes.apps.metrics.abstract_models import (
    AbstractBrowser,
    AbstractEngine,
    AbstractPlatform,
    AbstractPage,
    AbstractPageView,
    AbstractReferrer,
    AbstractReferrerPage,
    AbstractVisit,
    AbstractVisitor,
)

class Browser(AbstractBrowser):
    pass

class Engine(AbstractEngine):
    pass

class Platform(AbstractPlatform):
    pass

class Page(AbstractPage):
    pass

class PageView(AbstractPageView):
    pass

class Referrer(AbstractReferrer):
    pass

class ReferrerPage(AbstractReferrerPage):
    pass

class Visit(AbstractVisit):
    pass

class Visitor(AbstractVisitor):
    pass
