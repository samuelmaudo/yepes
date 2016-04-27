# -*- coding:utf-8 -*-

from yepes.apps import AppConfig, apps
from yepes.utils.properties import cached_property


class OverridableConfig(AppConfig):
    """
    Class representing a Django application and its configuration.
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
            if app_config.overrided_app_config.label == self.label
        ]

