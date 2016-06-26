# -*- coding:utf-8 -*-

from yepes.apps import OverridingConfig


class AppConfig(OverridingConfig):
    name = 'apps.invalid_target'
    overridden_app_label = 'non_overridable'

