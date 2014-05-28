# -*- coding:utf-8 -*-

from django import template

VERBOSE_NAME = 'Yepes'
VERSION = (0, 1, 0, 'alpha', 1)

def get_version():
    from django.utils.version import get_version
    return get_version(VERSION)

template.add_to_builtins('yepes.defaultfilters')
template.add_to_builtins('yepes.defaulttags')
