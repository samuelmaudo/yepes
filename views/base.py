# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from django.views.generic.base import TemplateView
from yepes.view_mixins import CacheMixin


class CachedTemplateView(CacheMixin, TemplateView):
    pass

