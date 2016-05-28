# -*- coding:utf-8 -*-

from __future__ import unicode_literals

import types

from django.apps import AppConfig
from django.utils import six

from yepes.utils.modules import import_module


def get_class(self, module_name, class_name):
    """
    Dynamically imports a single class from the given ``module_name``.

    This is very similar to ``AppConfig.get_model()`` method but this
    method is more general though as it can load any class from the
    matching app, not just a model.

    Raises LookupError if the app does not contain the specified module
    or if the requested class cannot be found in the module.

    """
    module_path = '.'.join((self.module.__name__, module_name))
    module = import_module(module_path, ignore_missing=True)
    if module is None:
        msg = "Module '{0}.{1}' could not be found."
        raise LookupError(msg.format(self.label, module_name))

    try:
        return getattr(module, class_name)
    except AttributeError:
        msg = "Class '{0}' could not be found in '{1}.{2}'."
        raise LookupError(msg.format(class_name, self.label, module_name))

if six.PY2:
    get_class = types.MethodType(get_class, None, AppConfig)

setattr(AppConfig, 'get_class', get_class)

