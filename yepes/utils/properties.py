# -*- coding:utf-8 -*-

from __future__ import unicode_literals


class cached_property(object):
    """
    Decorator that converts a method with a single ``self`` argument into a
    property cached on the instance.

    Optional ``name`` argument allows you to make cached properties of other
    methods. For example::

        url = cached_property(get_absolute_url, name='url')

    NOTE: Django implements a similar decorator but this follows more closely
    the code of standard Python properties.

    """
    def __init__(self, fget, name=None, doc=None):
        self.fget = fget
        self.name = name if name is not None else fget.__name__
        self.__doc__ = doc if doc is not None else fget.__doc__

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        else:
            value = obj.__dict__[self.name] = self.fget(obj)
            return value


class class_property(property):
    """
    Decorator that converts a class method with a single ``cls`` argument into
    a class property.
    """
    def __get__(self, obj, objtype=None):
        if obj is None:
            return self.fget(objtype)
        else:
            raise AttributeError('unreadable attribute')


def described_property(short_description, allow_tags=False, boolean=False,
                       cached=False, doc=None):
    """
    Decorator that adds a ``short_description`` to a method with a single
    ``self`` argument and converts it into a property. Is intended to allow
    model properties to be displayed on admin with a verbose name (the short
    description).

    Set optional ``allow_tags`` argument as True disables HTML escaping,
    letting you to use HTML tags in the description.

    Set optional ``boolean`` argument as True causes admin interface displays
    a pretty on/off icon instead of just show "True" or "False".

    Set optional ``cached`` argument as True causes method is converted into
    a cached property instead of a standard property, that is the default
    behavior.

    """
    def decorator(func):
        func.short_description = short_description
        func.allow_tags = bool(allow_tags)
        func.boolean = bool(boolean)
        if cached:
            return cached_property(func, doc=doc)
        else:
            return property(func, doc=doc)

    return decorator

