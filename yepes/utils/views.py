# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from functools import wraps


def decorate_view(*decorator_list):

    decorator_list = tuple(reversed(decorator_list))

    def class_decorator(cls):

        _dispatch = cls.dispatch
        def dispatch_wrapper(self, *args, **kwargs):
            def internal_wrapper(*args2, **kwargs2):
                return _dispatch(self, *args2, **kwargs2)
            for decorator in decorator_list:
                internal_wrapper = decorator(internal_wrapper)
            return internal_wrapper(*args, **kwargs)

        cls.dispatch = wraps(_dispatch)(dispatch_wrapper)
        return cls

    return class_decorator

