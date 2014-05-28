# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from django.db import models
from django.utils.translation import ugettext_lazy as _

from yepes import managers

__all__ = ('Enableable', )


class Enableable(models.Model):

    ENABLED = True
    DISABLED = False
    ENABLE_CHOICES = (
        (ENABLED, _('Enabled')),
        (DISABLED, _('Disabled')),
    )

    is_enabled = models.BooleanField(
            choices=ENABLE_CHOICES,
            default=ENABLED,
            db_index=True,
            verbose_name=_('Status'))

    objects = managers.EnableableManager()

    class Meta:
        abstract = True

