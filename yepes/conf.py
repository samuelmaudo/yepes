# -*- coding:utf-8 -*-

from __future__ import unicode_literals

import importlib

from django.conf import settings as user_settings
from django.utils import six


class DebugSettings(object):

    def __init__(self):

        self.__dict__['_default_settings'] = {}
        self.__dict__['_user_settings'] = user_settings

        for app in user_settings.INSTALLED_APPS:
            module_name = '{0}.settings'.format(app)
            try:
                default_settings = importlib.import_module(module_name)
            except ImportError:
                pass
            else:
                for name, value in six.iteritems(vars(default_settings)):
                    if name.isupper():
                        self._default_settings[name] = value

    def __getattribute__(self, name):
        if name.startswith('_'):
            return object.__getattribute__(self, name)
        try:
            return getattr(self._user_settings, name)
        except AttributeError:
            try:
                return self._default_settings[name]
            except KeyError:
                args = [
                    self.__class__.__name__,
                    name,
                ]
                msg = "'{0}' object has no attribute '{1}'"
                raise AttributeError(msg.format(*args))

    def __setattr__(self, name, value):
        msg = "can't set attribute '{0}'"
        raise AttributeError(msg.format(name))


class ProductionSettings(object):

    def __init__(self):

        for app in user_settings.INSTALLED_APPS:
            module_name = '{0}.settings'.format(app)
            try:
                default_settings = importlib.import_module(module_name)
            except ImportError:
                pass
            else:
                for name, value in six.iteritems(vars(default_settings)):
                    if name.isupper():
                        self.__dict__[name] = value

        for name, value in six.iteritems(vars(user_settings._wrapped)):
            if name.isupper():
                self.__dict__[name] = value

    def __setattr__(self, name, value):
        msg = "can't set attribute '{0}'"
        raise AttributeError(msg.format(name))


if user_settings.DEBUG:
    settings = DebugSettings()
else:
    settings = ProductionSettings()

