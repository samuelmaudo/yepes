# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from django.utils import six

from yepes.apps.thumbnails.exceptions import ConfigDoesNotExist
from yepes.exceptions import UnexpectedTypeError
from yepes.loading import get_model


def clean_config(value):

    Configuration = get_model('thumbnails', 'Configuration')

    if isinstance(value, Configuration):
        return value

    if isinstance(value, six.text_type):
        config = Configuration.cache.get(key=value)
        if config is None:
            raise ConfigDoesNotExist(value)
        else:
            return config

    raise UnexpectedTypeError([Configuration, six.text_type], type(value))

