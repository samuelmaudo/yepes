# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from django.db.models import Model
from django.utils import six

from yepes.apps import apps
from yepes.exceptions import UnexpectedTypeError
from yepes.loading import LazyModel

Site = LazyModel('sites', 'Site')


def get_model(info):
    if isinstance(info, Model):
        return info

    if isinstance(info, six.string_types):
        model = apps.get_model(info)
    elif isinstance(info, (tuple, list)):
        model = apps.get_model(*info)
    elif isinstance(info, dict):
        model = apps.get_model(**info)
    else:
        raise UnexpectedTypeError((str, list, dict), info)

    return model


def get_queryset(info):
    model = get_model(info)
    return model._default_manager.get_queryset()


def get_site(site_id=None):
    if site_id is None:
        return Site.objects.get_current()
    else:
        return Site.objects._get_site_by_id(site_id)

