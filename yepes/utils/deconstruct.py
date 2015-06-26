# -*- coding:utf-8 -*-

from __future__ import unicode_literals

import collections

from django.utils import six


def clean_keywords(obj, keywords, defaults=None, overrides=None, immutables=None):
    if defaults is not None:
        if overrides is None:
            overrides = {}

        for name, default in six.iteritems(defaults):
            discard = True
            value = getattr(self, overrides.get(name, name))
            if value is not default:
                if not isinstance(default, collections.Iterable):
                    discard = False
                    keywords[name] = value
                elif isinstance(value, collections.Iterable):
                    default = list(default)
                    value = list(value)
                    if value != default:
                        discard = False
                        keywords[name] = value

            if discard:
                keywords.pop(name, None)

    if immutables is not None:
        for name in immutables:
            keywords.pop(name, None)

