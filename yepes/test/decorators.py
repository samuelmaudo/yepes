# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from functools import wraps

from django.utils import six

from yepes.contrib.registry import registry

__all__ = ('override_registry', )


class override_registry(object):
    """
    Acts as either a decorator, or a context manager. If it's a decorator it
    takes a function and returns a wrapped function. If it's a contextmanager
    it's used with the ``with`` statement. In either event entering/exiting
    are called before and after, respectively, the function/block is executed.
    """
    def __init__(self, values):
        self.new_values = values

    def __enter__(self):
        self.enable()

    def __exit__(self, exc_type, exc_value, traceback):
        self.disable()

    def __call__(self, test_func):
        from django.test import SimpleTestCase
        if isinstance(test_func, type):
            if not issubclass(test_func, SimpleTestCase):
                msg = ('Only subclasses of Django SimpleTestCase can be'
                       ' decorated with override_registry')
                raise Exception(msg)

            original_pre_setup = test_func._pre_setup
            original_post_teardown = test_func._post_teardown

            def _pre_setup(innerself):
                self.enable()
                original_pre_setup(innerself)

            def _post_teardown(innerself):
                original_post_teardown(innerself)
                self.disable()

            test_func._pre_setup = _pre_setup
            test_func._post_teardown = _post_teardown
            return test_func
        else:
            @wraps(test_func)
            def inner(*args, **kwargs):
                with self:
                    return test_func(*args, **kwargs)

        return inner

    def enable(self):
        self.old_values = {
            key: registry.get(key)
            for key
            in six.iterkeys(self.new_values)
        }
        for key, value in six.iteritems(self.new_values):
            registry[key] = value

    def disable(self):
        for key, value in six.iteritems(self.old_values):
            registry[key] = value

        del self.old_values

