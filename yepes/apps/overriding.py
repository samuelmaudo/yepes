# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from django.core.exceptions import ImproperlyConfigured

from yepes.apps import AppConfig, apps
from yepes.utils.properties import cached_property


class OverridingConfig(AppConfig):
    """
    Class representing a Django application which overrides another app.

    To achieve this, the overriding apps should be listed before the
    overridden application. This is because the first model registered
    prevails over the following models.

    """
    overridden_app_label = None

    @cached_property
    def overridden_app_config(self):
        return self.get_overridden_app_config()

    def __init__(self, app_name, app_module):
        super(OverridingConfig, self).__init__(app_name, app_module)
        self.original_label = self.label

    def get_overridden_app_config(self):
        if not self.overridden_app_label:
            msg = (
                '{cls} is missing a target. '
                'Define {cls}.overridden_app_label '
                'or override {cls}.get_overridden_app_config().'
            )
            raise ImproperlyConfigured(msg.format(cls=self.__class__.__name__))

        from yepes.apps import OverridableConfig
        app_config = apps.get_app_config(self.overridden_app_label)
        if not isinstance(app_config, OverridableConfig):
            msg = '{cls} is not overridable.'
            raise ImproperlyConfigured(msg.format(cls=app_config.__class__.__name__))

        return app_config

    def import_models(self, all_models):
        self.label = self.overridden_app_config.label
        super(OverridingConfig, self).import_models(all_models)

    def ready(self):
        super(OverridingConfig, self).ready()
        self.label = self.original_label
        self.__dict__['overridden_app_config'] = self.get_overridden_app_config()
