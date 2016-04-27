# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _

from yepes.apps import OverridableConfig


class NewslettersConfig(OverridableConfig):
    name = 'yepes.contrib.newsletters'
    verbose_name = _('Newsletters')

