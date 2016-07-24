# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class SitemapsConfig(AppConfig):
    name = 'yepes.contrib.sitemaps'
    verbose_name = _('Sitemaps')

