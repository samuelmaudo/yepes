# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from yepes.apps import AppConfig, apps
from yepes.utils.properties import cached_property


class OverridableConfig(AppConfig):
    """
    Class representing a Django application which can be overridden by
    defining an overriding app that points to it.

    To allow this, the overriding apps should be listed before the
    overridden application. This is because the first model registered
    prevails over the following models.

    """
    @cached_property
    def overriding_app_configs(self):
        return self.get_overriding_app_configs()

    def get_class(self, module_path, class_name):
        for app_config in self.overriding_app_configs:
            try:
                return app_config.get_class(module_path, class_name)
            except LookupError:
                pass

        return super(OverridableConfig, self).get_class(module_path, class_name)

    def get_overriding_app_configs(self):
        return [
            app_config
            for app_config
            in apps.get_overriding_app_configs()
            if app_config.overridden_app_config.label == self.label
        ]

    def ready(self):
        super(OverridableConfig, self).ready()
        self.__dict__.pop('overriding_app_configs', None)

