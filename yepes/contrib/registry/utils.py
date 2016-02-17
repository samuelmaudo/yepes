# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from django.db.models.base import Model
from django.db.models.loading import cache as models_cache
from django.contrib.sites.models import Site, SITE_CACHE
from django.utils import six


class InvalidInfo(TypeError):

    def __init__(self, info):
        msg = "A string, a list or a dictionary was expected, '{0!r}' received."
        super(InvalidInfo, self).__init__(msg.format(info))


class ModelNotFound(ValueError):

    def __init__(self, info):
        msg = "Not model was found for '{0}.{1}'."
        if isinstance(info, dict):
            info = (info['app_label'], info['model_name'])
        super(ModelNotFound, self).__init__(msg.format(*info))


def get_model(info):
    if isinstance(info, Model):
        return info
    if isinstance(info, six.string_types):
        tokens = info.split('.')
        info = (tokens[-2], tokens[-1])
    if isinstance(info, (tuple, list)):
        model = models_cache.get_model(*info)
    elif isinstance(info, dict):
        model = models_cache.get_model(**info)
    else:
        raise InvalidInfo(info)
    if not model:
        raise ModelNotFound(info)
    return model


def get_queryset(info):
    model = get_model(info)
    return model._default_manager.get_queryset()


def get_site(site_id):
    try:
        site = SITE_CACHE[site_id]
    except KeyError:
        site = Site.objects.get(pk=site_id)
        SITE_CACHE[site_id] = site
    return site

