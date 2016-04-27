# -*- coding:utf-8 -*-

from __future__ import unicode_literals

VERSION = (1, 0, 0, 'alpha', 0)

def get_version():
    from django.utils.version import get_version
    return get_version(VERSION)

default_app_config = 'yepes.contrib.slugs.apps.SlugsConfig'
