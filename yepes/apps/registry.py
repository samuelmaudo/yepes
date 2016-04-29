# -*- coding:utf-8 -*-

from __future__ import unicode_literals

import types
import warnings

from django.apps import apps
from django.apps.registry import Apps
from django.utils import six
from django.utils.lru_cache import lru_cache


def clear_cache(self):
    """
    Clears all internal caches, for methods that alter the app registry.

    This is mostly used in tests.

    """
    self.get_models.cache_clear()
    self.get_overriding_app_configs.cache_clear()

    # Call expire cache on each model. This will purge the
    # relation tree and the fields cache.
    if self.ready:
        for model in self.get_models(include_auto_created=True):
            model._meta._expire_cache()

if six.PY2:
    clear_cache = types.MethodType(clear_cache, None, Apps)

setattr(Apps, 'clear_cache', clear_cache)


def get_class(self, module_path, class_name=None):
    """
    Dynamically imports a single class from the given module_path. The
    path includes the app label and the module name, separated by a dot.
    E.g., 'yepes.views'.

    As a shortcut, this function also accepts a single argument in the
    form <module_path>.<class_name>.

    Raises LookupError if no application exists with the given label, or
    the app does not contain the specified module, or if the requested
    class cannot be found in the module. Raises ValueError if called
    with a single argument that doesn't contain exactly one dot.

    """
    if class_name is None:
        module_path, class_name = module_path.rsplit('.', 1)

    app_label, module_name = module_path.split('.', 1)
    return self.get_app_config(app_label).get_class(module_name, class_name)

if six.PY2:
    get_class = types.MethodType(get_class, None, Apps)

setattr(Apps, 'get_class', get_class)


@lru_cache(maxsize=None)
def get_overriding_app_configs(self):
    """
    Returns a list of all overriding app configs.
    """
    from yepes.apps import OverridingConfig
    return [
        app_config
        for app_config
        in apps.get_app_configs()
        if isinstance(app_config, OverridingConfig)
    ]

if six.PY2:
    get_overriding_app_configs = types.MethodType(get_overriding_app_configs, None, Apps)

setattr(Apps, 'get_overriding_app_configs', get_overriding_app_configs)


def register_model(self, app_label, model):
    """
    Adds the given model to the registry. Models which are already
    registered, will be ignored. This is because overriding models need
    to prevail over overridden models. And because reloading models can
    lead to inconsistencies, most notably with related models.
    """
    # Since this method is called when models are imported, it cannot
    # perform imports because of the risk of import loops. It mustn't
    # call get_app_config().
    model_name = model._meta.model_name
    app_models = self.all_models[app_label]
    registered_model = app_models.get(model_name)
    if registered_model is not None:
        if (model.__name__ == registered_model.__name__
                and model.__module__ == registered_model.__module__):
            msg = "Model '{0}.{1}' was already registered."
            args = (app_label, model_name)
        else:
            msg = "Model '{0}.{1}' was already registered. '{2}' is discarded."
            args = (app_label, model_name, model.__name__)

        warnings.warn(msg.format(*args), RuntimeWarning, stacklevel=2)
    else:
        app_models[model_name] = model
        self.clear_cache()

if six.PY2:
    register_model = types.MethodType(register_model, None, Apps)

setattr(Apps, 'register_model', register_model)

