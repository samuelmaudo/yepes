# -*- coding:utf-8 -*-

from __future__ import unicode_literals

import os

from django.core.exceptions import ImproperlyConfigured
from django.db import models
import django.db.models.options as options
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _

from yepes import fields

__all__ = ('Illustrated', )


options.DEFAULT_NAMES = options.DEFAULT_NAMES + ('folder_name', )


def image_upload_to(instance, filename):
    return instance.get_upload_path(filename)


@python_2_unicode_compatible
class Illustrated(models.Model):

    image = fields.ImageField(
            blank=True,
            max_length=127,
            height_field='image_height',
            width_field='image_width',
            upload_to=image_upload_to,
            verbose_name=_('Image'))
    image_height = models.PositiveIntegerField(
            editable=False,
            blank=True,
            null=True,
            verbose_name=_('Image Height'))
    image_width = models.PositiveIntegerField(
            editable=False,
            blank=True,
            null=True,
            verbose_name=_('Image Width'))

    class Meta:
        abstract = True

    def __str__(self):
        return os.path.basename(self.image.name)

    def get_upload_path(self, filename):
        foldername = getattr(self._meta, 'folder_name', None)
        if not foldername:
            msg = 'You must set a ``folder_name`` in the model Meta class.'
            raise ImproperlyConfigured(msg)
        else:
            return os.path.join(foldername, filename[0], filename)

