# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from django.db.models.fields.files import ImageField as BaseImageField

from yepes.apps.thumbnails.files import SourceFieldFile
from yepes.forms.widgets import ImageWidget


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

    def formfield(self, **kwargs):
        kwargs['widget'] = ImageWidget
        return super(ImageField, self).formfield(**kwargs)

    def south_field_triple(self):
        """
        Return a suitable description of this field for South.
        """
        from south.modelsinspector import introspector
        field_class = 'django.db.models.fields.files.ImageField'
        args, kwargs = introspector(self)
        return (field_class, args, kwargs)

