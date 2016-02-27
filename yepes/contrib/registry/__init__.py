# -*- coding:utf-8 -*-

from django.utils.translation import ugettext_lazy as _

VERBOSE_NAME = _('Registry')
VERSION = (0, 1, 0, 'alpha', 1)

def get_version():
    from django.utils.version import get_version
    return get_version(VERSION)


def autodiscover():
    """
    Auto-discover INSTALLED_APPS registry.py modules and fail silently when
    not present. This forces an import on them to register any entries they
    may want.
    """
    import importlib
    from django.conf import settings
    for app in settings.INSTALLED_APPS:
        try:
            importlib.import_module('{0}.registry'.format(app))
        except ImportError:
            pass

from yepes.contrib.registry.base import *
autodiscover()
