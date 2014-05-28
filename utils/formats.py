# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from collections import namedtuple

from django.utils.formats import date_format

FakeDate = namedtuple('FakeDate', 'year, month, day')


def permissive_date_format(value, *args, **kwargs):
    """
    Like ``django.utils.formats.date_format()`` but accepts NULL as ``value``.
    """
    if value is None:
        value = FakeDate(0, 0, 0)

    return date_format(value, *args, **kwargs)

