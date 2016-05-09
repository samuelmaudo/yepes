# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from django.template.base import Library

from yepes.apps import apps
from yepes.template import AssignTag, SingleTag

ConfigurationProxy = apps.get_class('thumbnails.proxies', 'ConfigurationProxy')

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

        if force_generation:
            getter = source.generate_thumbnail
        else:
            getter = source.get_thumbnail

        try:
            return getter(config)
        except IOError:
            return None

    def render(self, context):
        if self.target_var is not None:
            old_value = context.get(self.target_var)
            if old_value is not None:
                # Probably we are into a loop and surely the old value will
                # not be used anymore, so we release memory.
                try:
                    old_value.close()
                except AttributeError:
                    pass

        return super(GetThumbnailTag, self).render(context)

register.tag('get_thumbnail', GetThumbnailTag.as_tag())


## {% make_configuration width height[ background[ mode[ algorithm[ gravity[ format[ quality]]]]]][ as variable_name] %} #####


class MakeConfigurationTag(AssignTag):
    """
    Returns a ``ConfigurationProxy`` instance with the specified parameters.
    """
    target_var = 'configuration'

    def process(self, width, height, background=None, mode='limit',
                      algorithm='undefined', gravity='center',
                      format='JPEG', quality=85):

        mode = mode.lower()
        algorithm = algorithm.lower()
        gravity = gravity.lower()
        format = format.upper()

        return ConfigurationProxy(**{
            'width': width,
            'height': height,
            'background': background,
            'mode': mode,
            'algorithm': algorithm,
            'gravity': gravity,
            'format': format if format != 'PNG' else 'PNG64',
            'quality': quality,
        })

register.tag('make_configuration', MakeConfigurationTag.as_tag())


## {% thumbnail_tag source config **attrs %} ###################################


class ThumbnailTagTag(SingleTag):
    """
    Gets the thumbnail of the ``source`` image that matches the given ``config``
    and renders an <img> tag for it.
    """
    def process(self, source, config, **attrs):
        if source:
            was_closed = source.closed
            try:
                thumbnail = source.get_thumbnail(config)
            except IOError:
                return ''

            thumbnail_tag = thumbnail.get_tag(**attrs)
            thumbnail.close()
            if was_closed:
                source.close()

            return thumbnail_tag
        else:
            return ''

register.tag('thumbnail_tag', ThumbnailTagTag.as_tag())


## {% thumbnail_url source config %} ###########################################


class ThumbnailUrlTag(SingleTag):
    """
    Gets the thumbnail of the ``source`` image that matches the given ``config``
    and renders its url.
    """
    def process(self, source, config):
        if source:
            was_closed = source.closed
            try:
                thumbnail = source.get_thumbnail(config)
            except IOError:
                return ''

            thumbnail_url = thumbnail.url
            thumbnail.close()
            if was_closed:
                source.close()

            return thumbnail_url
        else:
            return ''

register.tag('thumbnail_url', ThumbnailUrlTag.as_tag())

