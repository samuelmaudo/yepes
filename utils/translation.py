# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy


def translatable_property(description):
    """
    Decorator that adds a translatable description to a method with a single
    self argument and converts it into a property.
    """
    def decorator(func):
        func.short_description = ugettext_lazy(description)
        return property(func)

    return decorator

