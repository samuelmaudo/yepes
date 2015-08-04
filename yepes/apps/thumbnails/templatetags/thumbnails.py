# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from django.template.base import Library

from yepes.apps.thumbnails.proxies import ConfigurationProxy
from yepes.template import AssignTag

register = Library()


## {% get_thumbnail source config[ as variable_name] %} ########################


class GetThumbnailTag(AssignTag):
    """
    Returns a thumbnail of the ``source`` image with the given ``config``.

    If a matching thumbnail already exists, it will simply be returned.
    Otherwise, a new thumbnail is generated.

    """
    target_var = 'thumbnail'

    @classmethod
    def get_syntax(cls, tag_name='tag_name'):
        syntax = super(GetThumbnailTag, cls).get_syntax(tag_name)
        # `force_generation` parameter is only for internal tests.
        return syntax.replace('[ force_generation]', '')

    def process(self, source, config, force_generation=False):
        if not source:
            return None
        elif force_generation:
            return source.generate_thumbnail(config)
        else:
            return source.get_thumbnail(config)

register.tag('get_thumbnail', GetThumbnailTag.as_tag())


## {% make_thumbnail source width height[ filter[ blur[ format[ quality]]]][ as variable_name] %} #####


class MakeThumbnailTag(GetThumbnailTag):
    """
    Returns a thumbnail of the ``source`` image with the specified ``width``
    and ``height``.

    If a matching thumbnail already exists, it will simply be returned.
    Otherwise, a new thumbnail is generated.

    """
    def process(self, source, width, height, filter='undefined', blur=1.0,
                format='JPEG', quality=85, force_generation=False):

        if not source:
            return None

        config = ConfigurationProxy(**{
            'width': width,
            'height': height,
            'filter': filter,
            'blur': blur,
            'format': format,
            'quality': quality,
        })
        if force_generation:
            return source.generate_thumbnail(config)
        else:
            return source.get_thumbnail(config)

register.tag('make_thumbnail', MakeThumbnailTag.as_tag())

