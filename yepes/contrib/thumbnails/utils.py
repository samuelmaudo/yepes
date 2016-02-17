# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from django.utils import six

from yepes.contrib.thumbnails.exceptions import ConfigDoesNotExist
from yepes.exceptions import UnexpectedTypeError
from yepes.loading import LazyModel

Configuration = LazyModel('thumbnails', 'Configuration')


def clean_config(value):
    if isinstance(value, Configuration):
        return value
    elif isinstance(value, six.string_types):
        config = Configuration.cache.get(key=value)
        if config is None:
            raise ConfigDoesNotExist(value)
        else:
            return config
    else:
        raise UnexpectedTypeError((Configuration, six.text_type), value)

