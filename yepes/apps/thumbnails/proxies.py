# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from django.utils.encoding import python_2_unicode_compatible

from yepes.loading import LazyModel

Configuration = LazyModel('thumbnails', 'Configuration')


@python_2_unicode_compatible
class ConfigurationProxy(object):

    def __init__(self, width, height, **kwargs):
        self._wrapped = Configuration(width=width, height=height, **kwargs)

        tokens = []
        if self._wrapped.width:
            tokens.append('w{0}'.format(self._wrapped.width))

        if self._wrapped.height:
            tokens.append('h{0}'.format(self._wrapped.height))

        if self._wrapped.background:
            tokens.append('b{0}'.format(self._wrapped.background.lstrip('#', 1).upper()))

        if self._wrapped.mode != 'limit':
            tokens.append('m{0}'.format(self._wrapped.mode.upper()))

        if self._wrapped.algorithm != 'undefined':
            tokens.append('a{0}'.format(self._wrapped.algorithm.upper()))

        if self._wrapped.gravity != 'center':
            tokens.append('g{0}'.format(self._wrapped.gravity.replace('_', '').upper()))

        if self._wrapped.format != 'JPEG':
            tokens.append('f{0}'.format(self._wrapped.format.upper()))

        if self._wrapped.quality != 85:
            tokens.append('q{0}'.format(self._wrapped.quality))

        self._wrapped.key = '_'.join(tokens)
        self._wrapped.full_clean()

    def __str__(self):
        return self.key

    @property
    def __class__(self):
        return self._wrapped.__class__

    @property
    def key(self):
        return self._wrapped.key

    @property
    def width(self):
        return self._wrapped.width

    @property
    def height(self):
        return self._wrapped.height

    @property
    def background(self):
        return self._wrapped.background

    @property
    def mode(self):
        return self._wrapped.mode

    @property
    def algorithm(self):
        return self._wrapped.algorithm

    @property
    def gravity(self):
        return self._wrapped.gravity

    @property
    def format(self):
        return self._wrapped.format

    @property
    def quality(self):
        return self._wrapped.quality

