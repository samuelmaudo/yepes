# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from django.utils import six
from django.utils.encoding import force_str
from django.utils.functional import empty, LazyObject

from yepes.apps import apps
from yepes.utils.modules import import_module

__all__ = (
    'LoadingError', 'MissingAppError', 'MissingClassError',
    'MissingModelError', 'MissingModuleError', 'UnavailableAppError',
    'get_class', 'get_classes',
    'get_model', 'get_models',
    'get_module',
    'LazyClass',
    'LazyModel', 'LazyModelManager', 'LazyModelObject',
)


LoadingError = LookupError
MissingAppError = LookupError
MissingClassError = LookupError
MissingModelError = LookupError
MissingModuleError = LookupError
UnavailableAppError = LookupError


get_class = apps.get_class


def get_classes(module_path, class_names):
    """
    Dynamically import a list of classes from the given module.

    This works by looping over ``INSTALLED_APPS`` and looking for a match
    against the passed module path. If the requested classes cannot be found in
    the matching module, and error is raised.

    This is very similar to ``django.db.models.get_model()`` function for
    dynamically loading models. But this function is more general though as it
    can load any class from the matching app, not just a model.

    Args:

        module_path (str): Module path comprising the app label and the module
                           name, separated by a dot. E.g., 'registry.base'.

        class_names (list): Names of the classes to be imported.

    Returns:

        The requested classes.

    Example:

        >>> get_classes('registry.base', ['AlreadyRegisteredError',
                                          'UnregisteredError'])
        [<class 'yepes.contrib.registry.base.AlreadyRegisteredError'>,
         <class 'yepes.contrib.registry.base.UnregisteredError'>]

    Raises:

        MissingAppError: If no installed app matches the passed app label.

        MissingModuleError: If no app contains the specified module.

        MissingClassError: If one, or more, of the requested classes cannot be
                           found in any module.

    """
    app_label, module_path = module_path.split('.', 1)
    app_config = apps.get_app_config(app_label)
    return [
        app_config.get_class(module_path, class_name)
        for class_name
        in class_names
    ]


get_model = apps.get_model


def get_models(app_label=None, model_names=None):
    """
    Returns the models of the given app matching case-insensitive model names.

    This is very similar to ``django.db.models.get_model()`` function for
    dynamically loading models. But this function returns multiple models at
    the same time and raises appropriate errors if any model cannot be found.

    Args:

        app_label (str): Label of the app that contains the model. If None is
                passed, all models of all available apps will be returned.

        model_names (list): Names of the models to be retrieved. If None is
                passed, all models in the app will be returned.

    Returns:

        The requested model classes.

    Example:

        >>> get_models('registry', ['Entry', 'LongEntry'])
        [<class 'yepes.contrib.registry.models.Entry'>,
         <class 'yepes.contrib.registry.models.LongEntry'>]

    Raises:

        MissingAppError: If no installed app matches the given app label.

        UnavailableAppError: If app is not currently available.

        MissingModelError: If one of the requested models cannot be found.

    """
    if app_label is None:
        return list(apps.get_models())

    app_config = apps.get_app_config(app_label)
    if model_names is None:
        return list(app_config.get_models())
    else:
        return [
            app_config.get_model(name)
            for name
            in model_names
        ]


get_module = import_module


def is_installed(app_label):
    """
    Checks if it has installed an app with the given label.

    Args:

        app_label (str): Label of the app to check.

    Returns:

        True if the app is installed or False if not.

    Example:

        >>> is_installed('registry')
        True

    """
    return app_label in apps


class LazyClass(LazyObject):

    def __init__(self, module_path, class_name):
        self.__dict__['_module_path'] = module_path
        self.__dict__['_class_name'] = class_name
        super(LazyClass, self).__init__()

    def _setup(self):
        self._wrapped = apps.get_class(self._module_path, self._class_name)

    def __repr__(self):
        # We have to use type(self), not self.__class__, because the latter
        # is proxied.
        class_name = type(self).__name__
        wrapped_class = (self._module_path, self._class_name)
        return force_str('<{0}: {1}>'.format(class_name, '.'.join(wrapped_class)))

    def __call__(self, *args, **kwargs):
        if self._wrapped is empty:
            self._setup()
        return self._wrapped.__call__(*args, **kwargs)

    def __instancecheck__(self, instance):
        if self._wrapped is empty:
            self._setup()
        return self._wrapped.__instancecheck__(instance)

    def __subclasscheck__(self, subclass):
        if self._wrapped is empty:
            self._setup()
        return self._wrapped.__subclasscheck__(subclass)


class LazyModel(LazyObject):

    def __init__(self, app_label, model_name):
        self.__dict__['_app_label'] = app_label
        self.__dict__['_model_name'] = model_name
        super(LazyModel, self).__init__()

    def _setup(self):
        self._wrapped = apps.get_model(self._app_label, self._model_name)

    def __repr__(self):
        # We have to use type(self), not self.__class__, because the latter
        # is proxied.
        class_name = type(self).__name__
        wrapped_model = (self._app_label, self._model_name)
        return force_str('<{0}: {1}>'.format(class_name, '.'.join(wrapped_model)))

    def __call__(self, *args, **kwargs):
        if self._wrapped is empty:
            self._setup()
        return self._wrapped.__call__(*args, **kwargs)

    def __instancecheck__(self, instance):
        if self._wrapped is empty:
            self._setup()
        return self._wrapped.__instancecheck__(instance)

    def __subclasscheck__(self, subclass):
        if self._wrapped is empty:
            self._setup()
        return self._wrapped.__subclasscheck__(subclass)


class LazyModelManager(LazyObject):

    def __init__(self, app_label, model_name, manager=None):
        self.__dict__['_app_label'] = app_label
        self.__dict__['_model_name'] = model_name
        self.__dict__['_manager'] = manager
        super(LazyModelManager, self).__init__()

    def _setup(self):
        model = apps.get_model(self._app_label, self._model_name)
        if self._manager is None:
            self._wrapped = model._default_manager
        else:
            self._wrapped = getattr(model, self._manager)

    def __repr__(self):
        # We have to use type(self), not self.__class__, because the latter
        # is proxied.
        class_name = type(self).__name__
        wrapped_manager = [self._app_label, self._model_name]
        if self._manager is not None:
            wrapped_manager.append(self._manager)

        return force_str('<{0}: {1}>'.format(class_name, '.'.join(wrapped_manager)))


class LazyModelObject(LazyObject):

    def __init__(self, model, manager=None, **lookup_parameters):
        self.__dict__['_model'] = model
        self.__dict__['_manager'] = manager
        self.__dict__['_lookup_parameters'] = lookup_parameters
        super(LazyModelObject, self).__init__()

    def _setup(self):
        model = self._model
        if isinstance(model, six.string_types):
            model = apps.get_model(*model.rsplit('.', 1))

        if self._manager is None:
            manager = model._default_manager
        else:
            manager = getattr(model, self._manager)

        self._wrapped = manager.get(**self._lookup_parameters)

    def __repr__(self):
        # We have to use type(self), not self.__class__, because the latter
        # is proxied.
        class_name = type(self).__name__
        try:
            wrapped_object = six.text_type(self)
        except UnicodeError:
            wrapped_object = '[Bad Unicode data]'

        return force_str('<{0}: {1}>'.format(class_name, wrapped_object))

