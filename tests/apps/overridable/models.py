# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from yepes.apps import apps

AbstractArticle = apps.get_class('overridable.abstract_models', 'AbstractArticle')
AbstractAuthor = apps.get_class('overridable.abstract_models', 'AbstractAuthor')


class Article(AbstractArticle):
    pass


class Author(AbstractAuthor):
    pass

