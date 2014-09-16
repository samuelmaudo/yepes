# -*- coding:utf-8 -*-

from __future__ import unicode_literals


class cached_property(object):
    """
    Decorator that converts a method with a single self argument into a
    property cached on the instance.
    """
    def __init__(self, func):
        self.fget = func
        self.__doc__ = func.__doc__

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        else:
            value = obj.__dict__[self.fget.__name__] = self.fget(obj)
            return value


class class_property(property):

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self.fget(objtype)
        else:
            raise AttributeError('unreadable attribute')


def described_property(description, allow_tags=False,
                       boolean=False, cached=False):
    """
    Decorator that adds a short description to a method with a single self
    argument and converts it into a property.
    """
    def decorator(func):
        func.short_description = description
        func.allow_tags = bool(allow_tags)
        func.boolean = bool(boolean)
        if cached:
            return cached_property(func)
        else:
            return property(func)

    return decorator

