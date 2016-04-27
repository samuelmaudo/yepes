# -*- coding:utf-8 -*-

from yepes.apps import OverridingConfig


class AppConfig(OverridingConfig):
    name = 'tests.apps.overriding'
    overrided_app_label = 'overridable'

