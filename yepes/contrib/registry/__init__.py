# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from yepes.contrib.registry.base import *

def autodiscover():
    """
    Auto-discover INSTALLED_APPS registry.py modules and fail silently when
    not present. This forces an import on them to register any entries they
    may want.
    """
    from yepes.apps import apps
    from yepes.utils.modules import import_module
    for app_config in apps.get_app_configs():
        module_path = '.'.join((app_config.name, 'registry'))
        import_module(module_path, ignore_missing=True)

default_app_config = 'yepes.contrib.registry.apps.RegistryConfig'
