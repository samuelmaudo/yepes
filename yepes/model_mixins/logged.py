# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from django.db import models
from django.utils.translation import ugettext_lazy as _

__all__ = ('Logged', )


class Logged(models.Model):

    creation_date = models.DateTimeField(
            auto_now_add=True,
            editable=False,
            verbose_name=_('Creation Date'))
    last_modified = models.DateTimeField(
            auto_now=True,
            editable=False,
            verbose_name=_('Last Modified'))

    class Meta:
        abstract = True

    def save(self, **kwargs):
        update_fields = kwargs.get('update_fields')
        if update_fields is not None:
            update_fields = set(update_fields)
            update_fields.add('last_modified')
            kwargs['update_fields'] = update_fields
        super(Logged, self).save(**kwargs)

