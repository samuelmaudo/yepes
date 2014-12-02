# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from yepes import managers

__all__ = ('Activatable', )


class Activatable(models.Model):

    ACTIVE = True
    INACTIVE = False
    ACTIVE_CHOICES = (
        (ACTIVE, _('Active')),
        (INACTIVE, _('Inactive')),
    )

    active_status = models.BooleanField(
            choices=ACTIVE_CHOICES,
            default=ACTIVE,
            db_index=True,
            verbose_name=_('Status'))
    active_from = models.DateTimeField(
            blank=True,
            null=True,
            verbose_name=_('Active From'),
            help_text=_("Won't be active until this time."))
    active_to = models.DateTimeField(
            blank=True,
            null=True,
            verbose_name=_('To'),
            help_text=_("Won't be active after this time."))

    objects = managers.ActivatableManager()

    class Meta:
        abstract = True

    def clean(self):
        super(Activatable, self).clean()
        if (self.active_from and self.active_to
                and self.active_to < self.active_from):
            msg = _('End date cannot be earlier than starting date.')
            raise ValidationError(msg)

    def is_active(self, date=None):
        if date is None:
            date = timezone.now()
        return (self.active_status == Activatable.ACTIVE
                and (self.active_from is None or self.active_from <= date)
                and (self.active_to is None or self.active_to >= date))
    is_active.boolean = True
    is_active.short_description = _('Is Active?')

