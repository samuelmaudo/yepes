# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from django.db.models import ImageField as BaseImageField

from yepes.contrib.thumbnails.files import SourceFieldFile
from yepes.forms.widgets import ImageWidget
from yepes.utils.deconstruct import clean_keywords


class ImageField(BaseImageField):
    """
    An image field which provides easier access for retrieving
    (and generating) thumbnails.

    To use a different file storage for thumbnails, provide the
    ``thumbnail_storage`` keyword argument.

    """
    attr_class = SourceFieldFile

    def __init__(self, *args, **kwargs):
        # Arguments not explicitly defined so that the normal ImageField
        # positional arguments can be used.
        self.thumbnail_storage = kwargs.pop('thumbnail_storage', None)
        super(ImageField, self).__init__(*args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super(ImageField, self).deconstruct()
        path = path.replace('yepes.contrib.thumbnails', 'yepes')
        clean_keywords(self, kwargs, variables={
            'thumbnail_storage': None,
        })
        return name, path, args, kwargs

    def formfield(self, **kwargs):
        kwargs['widget'] = ImageWidget
        return super(ImageField, self).formfield(**kwargs)

