# -*- coding:utf-8 -*-

from __future__ import unicode_literals

import collections

from django.utils import six


def clean_keywords(obj, keywords, variables=None, constants=None, overrides=None):
    if variables is not None:
        if overrides is None:
            overrides = {}

        for name, default in six.iteritems(variables):
            discard = True
            value = getattr(obj, overrides.get(name, name))
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

    if constants is not None:
        for name in constants:
            keywords.pop(name, None)

