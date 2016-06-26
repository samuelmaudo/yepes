# -*- coding:utf-8 -*-

from yepes.apps import OverridingConfig


class AppConfig(OverridingConfig):
    name = 'apps.overriding'
    overridden_app_label = 'overridable'

