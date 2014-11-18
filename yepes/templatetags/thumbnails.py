# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from django.template.base import Library

from yepes.template import AssignTag

register = Library()


## {% get_thumbnail source config [ as variable_name] %} #######################


class GetThumbnailTag(AssignTag):
    """
    Returns a thumbnail from a ``SourceFile``.

    If a matching thumbnail already exists, it will simply be returned.
    Otherwise, a new thumbnail is generated.

    """
    target_var = 'thumbnail'

    def process(self, source, config):
        if not source:
            return None
        else:
            return source.get_thumbnail(config)

register.tag('get_thumbnail', GetThumbnailTag.as_tag())

