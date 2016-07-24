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
        super(YepesConfig, self).ready()
        from django import VERSION as DJANGO_VERSION
        if DJANGO_VERSION < (1, 9):
            from django.template.base import add_to_builtins
            add_to_builtins('yepes.defaultfilters')
            add_to_builtins('yepes.defaulttags')
        else:
            from django.template.engine import Engine
            Engine.default_builtins.append('yepes.defaultfilters')
            Engine.default_builtins.append('yepes.defaulttags')

