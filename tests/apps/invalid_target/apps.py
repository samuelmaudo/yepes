# -*- coding:utf-8 -*-

from yepes.apps import OverridingConfig


class AppConfig(OverridingConfig):
    name = 'tests.apps.invalid_target'
    overrided_app_label = 'non_overridable'

