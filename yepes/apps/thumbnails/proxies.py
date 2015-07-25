# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from wand.image import FILTER_TYPES

from django.utils.encoding import python_2_unicode_compatible

from yepes.loading import get_model
from yepes.utils.properties import cached_property


@python_2_unicode_compatible
class ConfigurationProxy(object):

    FILTER_TYPES = tuple(FILTER_TYPES)
    FORMAT_TYPES = (
        'GIF',
        'JPEG',
        'PNG',
        'WEBP',
    )
    def __init__(self, width, height, filter='undefined', blur=1.0,
                       format='JPEG', quality=85):
        if not width or width < 0:
            raise ValueError
        else:
            self._width = int(width)

        if not height or height < 0:
            raise ValueError
        else:
            self._height = int(height)

        if filter not in self.FILTER_TYPES:
            raise ValueError
        else:
            self._filter = filter

        if not blur or blur < 0.0:
            raise ValueError
        else:
            self._blur = float(blur)

        if format not in self.FORMAT_TYPES:
            raise ValueError
        else:
            self._format = format

        if not quality or quality < 1 or quality > 100:
            raise ValueError
        else:
            self._quality = int(quality)

    def __str__(self):
        return self.key

    @property
    def key(self):
        k = 'w{0}_h{1}'.format(self._width, self._height)
        if self._blur != 1.0:
            k += '_b{0}'.format(self._blur)
        if self._quality != 85:
            k += '_q{0}'.format(self._quality)
        if self._filter != 'undefined':
            k += '_{0}'.format(self._filter)
        return k

    @property
    def width(self):
        return self._width

    @property
    def height(self):
        return self._height

    @property
    def filter(self):
        return self._filter

    @property
    def blur(self):
        return self._blur

    @property
    def format(self):
        return self._format

    @property
    def quality(self):
        return self._quality

    # Need to pretend to be the wrapped class, for the sake of objects that
    # care about this (especially in equality tests).
    @cached_property
    def __class__(self):
        return get_model('thumbnails', 'Configuration')

