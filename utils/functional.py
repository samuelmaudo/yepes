# -*- coding:utf-8 -*-

from __future__ import unicode_literals


def described_property(description):
    """
    Decorator that adds a short description to a method with a single self
    argument and converts it into a property.
    """
    def decorator(func):
        func.short_description = description
        return property(func)

    return decorator

