# -*- coding:utf-8 -*-

from __future__ import unicode_literals

import imp
import sys
import traceback
import warnings

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.db.models.loading import cache as models_cache
from django.utils import six
from django.utils.encoding import force_str
from django.utils.functional import empty

from yepes.types import Singleton
from yepes.utils.compat import LazyObject

__all__ = (
    'LoadingError', 'MissingAppError', 'MissingClassError',
    'MissingModelError', 'MissingModuleError', 'UnavailableAppError',
    'get_class', 'get_classes',
    'get_model', 'get_models',
    'get_module',
    'LazyClass',
    'LazyModel', 'LazyModelManager', 'LazyModelObject',
)


class LoadingError(ImportError):
    pass


class MissingAppError(LoadingError):

    def __init__(self, app_label):
        msg = "App with label '{0}' could not be found."
        super(MissingAppError, self).__init__(msg.format(app_label))


class MissingClassError(LoadingError):

    def __init__(self, class_name, app_label):
        args = (
            class_name,
            app_label,
        )
        msg = "Class '{0}' could not be found in '{1}'."
        super(MissingClassError, self).__init__(msg.format(*args))


class MissingModelError(LoadingError):

    def __init__(self, model_name, app_label):
        args = (
            model_name,
            app_label,
        )
        msg = "Model '{0}' could not be found in '{1}'."
        super(MissingModelError, self).__init__(msg.format(*args))


class MissingModuleError(LoadingError):

    def __init__(self, module_path):
        msg = "Module '{0}' could not be imported."
        super(MissingModuleError, self).__init__(msg.format(module_path))


class UnavailableAppError(LoadingError):

    def __init__(self, app_label):
        msg = "App with label '{0}' is not available."
        super(UnavailableAppError, self).__init__(msg.format(app_label))


class ClassCache(Singleton):
    """
    This class stores the labels and the fully qualified names (aka paths) of
    each installed app.

    This follows the singleton pattern and is intended only for internal use.

    """
    def __init__(self):
        self.installed_apps = []
        self.is_populated = False

    def _populate(self):
        """
        Fill in all the cache information. This method is threadsafe, in the
        sense that every caller will see the same state upon return, and if the
        cache is already initialised, it does no work.
        """
        if self.is_populated:
            return

        # Note that we want to use the import lock here - the app loading is in
        # many cases initiated implicitly by importing, and thus it is possible
        # to end up in deadlock when one thread initiates loading without
        # holding the importer lock and another thread then tries to import
        # something which also launches the app loading.
        imp.acquire_lock()
        try:
            if self.is_populated:
                return

            for app_path in settings.INSTALLED_APPS:
                try:
                    __import__(app_path)
                except ImportError:
                    msg = "App path '{0}' could not be imported"
                    raise ImproperlyConfigured(msg.format(app_path))
                else:
                    app_label = app_path.rsplit('.', 1)[-1]
                    self.installed_apps.append((app_label, app_path))

            self.is_populated = True
        finally:
            imp.release_lock()


classes_cache = ClassCache()


def get_class(module_path, class_name):
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
        <class 'yepes.apps.registry.base.Registry'>

    Raises:

        MissingAppError: If no installed app matches the passed app label.

        MissingModuleError: If no app contains the specified module.

        MissingClassError: If the requested class cannot be found in any module.

    """
    return get_classes(module_path, [class_name])[0]


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
        [<class 'yepes.apps.registry.base.AlreadyRegisteredError'>,
         <class 'yepes.apps.registry.base.UnregisteredError'>]

    Raises:

        MissingAppError: If no installed app matches the passed app label.

        MissingModuleError: If no app contains the specified module.

        MissingClassError: If one, or more, of the requested classes cannot be
                           found in any module.

    """
    classes_cache._populate()

    found_classes = {}
    module_path_tokens = module_path.split('.', 1)
    app_label = module_path_tokens[0]

    app_found = False
    module_found = False
    for label, path in classes_cache.installed_apps:

        if label != app_label:
            continue

        app_found = True

        module_path_tokens[0] = path
        module_full_path = '.'.join(module_path_tokens)
        module = get_module(module_full_path, ignore_missing=True)
        if module is None:
            continue

        module_found = True

        for class_name in class_names:
            if (class_name not in found_classes
                    and hasattr(module, class_name)):
                found_classes[class_name] = getattr(module, class_name)

    if not app_found:
        raise MissingAppError(app_label)

    if not module_found:
        raise MissingModuleError(module_path)

    classes = []
    for class_name in class_names:
        try:
            classes.append(found_classes[class_name])
        except KeyError:
            raise MissingClassError(class_name, app_label)

    return classes


def get_model(app_label, model_name):
    """
    Returns the model of the given app matching case-insensitive model name.

    This is equal to ``django.db.models.get_model()`` function for dynamically
    loading models. But this function raises an error if the model cannot be
    found rather than returning none.

    Args:

        app_label (str): Label of the app that contains the model.

        model_name (str): Name of the model to be retrieved.

    Returns:

        The requested model class.

    Example:

        >>> get_model('registry', 'Entry')
        <class 'yepes.apps.registry.models.Entry'>

    Raises:

        MissingAppError: If no installed app matches the passed app label.

        UnavailableAppError: If app is not currently available.

        MissingModelError: If the requested model cannot be found.

    """
    return get_models(app_label, [model_name])[0]


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

        >>> get_model('registry', ['Entry', 'LongEntry'])
        [<class 'yepes.apps.registry.models.Entry'>,
         <class 'yepes.apps.registry.models.LongEntry'>]

    Raises:

        MissingAppError: If no installed app matches the given app label.

        UnavailableAppError: If app is not currently available.

        MissingModelError: If one of the requested models cannot be found.

    """
    models_cache._populate()

    found_models = []
    if app_label is None:
        for app_models in six.itervalues(models_cache.app_models):
            found_models.extend(six.itervalues(app_models))
    else:

        if app_label not in models_cache.app_labels:
            raise MissingAppError(app_label)

        if (models_cache.available_apps is not None
                and app_label not in models_cache.available_apps):
            raise UnavailableAppError

        if model_names is None:
            try:
                app_models = models_cache.app_models[app_label]
            except KeyError:
                pass  # App has no models.
            else:
                found_models.extend(six.itervalues(app_models))
        else:
            for model_name in model_names:
                try:
                    model = models_cache.app_models[app_label][model_name.lower()]
                except KeyError:
                    raise MissingModelError(model_name, app_label)
                else:
                    found_models.append(model)

    return found_models


def get_module(module_path, ignore_missing=False, ignore_internal_errors=False):
    """
    Returns the module located at ``module_path``. If module had not been
    previously imported, tries to import it and add it to ``sys.modules``.

    This is similar to ``importlib.import_module()`` but this function allows
    to ignore certain import errors.

    Args:

        module_path (str): Name of the module to be retrieved.

        ignore_missing (bool): Whether ignore import errors when module is not
                found at the specified path. Defaults to False.

        ignore_internal_errors (bool): Whether ignore import errors when one of
                the module dependencies cannot be imported. Also ignores syntax
                errors and issues a warning when an error is ignored (this is
                for development purposes). Defaults to False.

    Returns:

        The requested module or None if an error occurs.

    Example:

        >>> get_module('yepes')
        <module 'yepes' from 'yepes/__init__.pyc'>

    Raises:

        MissingModuleError: If the requested module cannot be found and
                ``ignore_missing`` is False.

        ImportError: If a module dependency cannot be imported and
                ``ignore_internal_errors`` is False.

        SyntaxError: If module code has a syntax error and
                ``ignore_internal_errors`` is False.

    """
    try:
        __import__(module_path)
    except ImportError as e:
        """
        There are two reasons why there is ``ImportError``:
        1. The module does not exist at the specified path.
        2. The path is right, but one of the module dependencies cannot be
           imported.

        ``ImportError`` does not provide easy way to distinguish those two
        cases. Fortunately, the traceback of the ``ImportError`` starts at
        ``__import__`` statement. If the traceback has more than one entry,
        it means the path was correct and that is a subsequent dependence
        that generated the error.

        """
        error_type, error_value, error_traceback = sys.exc_info()
        stack_trace_entries = traceback.extract_tb(error_traceback)
        if len(stack_trace_entries) <= 1:
            if ignore_missing:
                return None
            else:
                raise MissingModuleError(module_path)
        else:
            if ignore_internal_errors:
                warnings.warn(str(e), ImportWarning, 2)
                return None
            else:
                raise e
    except SyntaxError as e:
        if ignore_internal_errors:
            warnings.warn(str(e), SyntaxWarning, 2)
            return None
        else:
            raise e

    return sys.modules[module_path]


class LazyClass(LazyObject):

    def __init__(self, module_path, class_name):
        self.__dict__['_module_path'] = module_path
        self.__dict__['_class_name'] = class_name
        super(LazyClass, self).__init__()

    def _setup(self):
        self._wrapped = get_class(self._module_path, self._class_name)

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
        self._wrapped = get_model(self._app_label, self._model_name)

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

    def __init__(self, app_label, model_name, manager_attr=None):
        self.__dict__['_app_label'] = app_label
        self.__dict__['_model_name'] = model_name
        self.__dict__['_manager_attr'] = manager_attr
        super(LazyModelManager, self).__init__()

    def _setup(self):
        model = get_model(self._app_label, self._model_name)
        if self._manager_attr is None:
            self._wrapped = model._default_manager
        else:
            self._wrapped = getattr(model, self._manager_attr)

    def __repr__(self):
        # We have to use type(self), not self.__class__, because the latter
        # is proxied.
        class_name = type(self).__name__
        wrapped_manager = [self._app_label, self._model_name]
        if self._manager_attr is not None:
            wrapped_manager.append(self._manager_attr)

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
            model = get_model(*model.rsplit('.', 1))

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

