# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from yepes.apps.config import AppConfig
from yepes.apps.registry import apps

from yepes.apps.overridable import OverridableConfig
from yepes.apps.overriding import OverridingConfig


class YepesConfig(AppConfig):

    name = 'yepes'
    verbose_name = 'Yepes'

    def ready(self):
        from django.template.base import add_to_builtins
        add_to_builtins('yepes.defaultfilters')
        add_to_builtins('yepes.defaulttags')

