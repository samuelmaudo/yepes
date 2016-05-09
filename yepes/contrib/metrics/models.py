# -*- coding:utf-8 -*-

from yepes.apps import apps

AbstractBrowser = apps.get_class('metrics.abstract_models', 'AbstractBrowser')
AbstractEngine = apps.get_class('metrics.abstract_models', 'AbstractEngine')
AbstractPlatform = apps.get_class('metrics.abstract_models', 'AbstractPlatform')
AbstractPage = apps.get_class('metrics.abstract_models', 'AbstractPage')
AbstractPageView = apps.get_class('metrics.abstract_models', 'AbstractPageView')
AbstractReferrer = apps.get_class('metrics.abstract_models', 'AbstractReferrer')
AbstractReferrerPage = apps.get_class('metrics.abstract_models', 'AbstractReferrerPage')
AbstractVisit = apps.get_class('metrics.abstract_models', 'AbstractVisit')
AbstractVisitor = apps.get_class('metrics.abstract_models', 'AbstractVisitor')


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

