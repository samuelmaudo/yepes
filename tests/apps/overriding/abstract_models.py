# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from django.db import models

from ..overridable.abstract_models import AbstractArticle as BaseArticle


class AbstractArticle(BaseArticle):

    extract = models.TextField(
            blank=True)

    class Meta:
        abstract = True

