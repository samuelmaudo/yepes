# -*- coding:utf-8 -*-

from yepes.apps import OverridingConfig


class AppConfig(OverridingConfig):
    name = 'tests.apps.missing_target'
    overrided_app_label = 'missing'

