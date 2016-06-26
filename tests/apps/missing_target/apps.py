# -*- coding:utf-8 -*-

from yepes.apps import OverridingConfig


class AppConfig(OverridingConfig):
    name = 'apps.missing_target'
    overridden_app_label = 'missing'

