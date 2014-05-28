# -*- coding:utf-8 -*-

from django.utils.translation import ugettext_lazy as _

VERBOSE_NAME = _('Standards')
VERSION = (0, 1, 0, 'alpha', 1)

def get_version():
    from django.utils.version import get_version
    return get_version(VERSION)
