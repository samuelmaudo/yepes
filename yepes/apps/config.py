# -*- coding:utf-8 -*-

from __future__ import unicode_literals

import types

from django.apps import AppConfig
from django.utils import six

from yepes.utils.modules import import_module


def get_class(self, module_path, class_name):
    """
    Returns the model with the given case-insensitive model_name.

    Raises LookupError if no model exists with this name.

    """
    """
    Dynamically import a single class from the given module.

    This is a simple wrapper around ``get_classes()`` for the case of loading a
    single class.

    Args:

        module_path (str): Module path comprising the app label and the module
                           name, separated by a dot. E.g., 'registry.base'.

        class_name (str): Name of the class to be imported.

    Returns:

        The requested class.

    Example:

        >>> get_class('registry.base', 'Registry')
        <class 'yepes.contrib.registry.base.Registry'>

    Raises:

        MissingAppError: If no installed app matches the passed app label.

        MissingModuleError: If no app contains the specified module.

        MissingClassError: If the requested class cannot be found in any module.

    """
    module_full_path = '.'.join((self.module.__name__, module_path))
    module = import_module(module_full_path, ignore_missing=True)
    if module is None:
        msg = "Module '{0}.{1}' could not be found."
        raise LookupError(msg.format(self.label, module_path))

    try:
        return getattr(module, class_name)
    except AttributeError:
        msg = "Class '{0}' could not be found in '{1}.{2}'."
        raise LookupError(msg.format(class_name, self.label, module_path))

if six.PY2:
    get_class = types.MethodType(get_class, None, AppConfig)

setattr(AppConfig, 'get_class', get_class)

