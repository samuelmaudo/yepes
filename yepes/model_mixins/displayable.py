# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from yepes import managers
from yepes.model_mixins import Slugged, MetaData

__all__ = ('Displayable', )


class Displayable(Slugged, MetaData):
    """
    Abstract model that provides features of a visible page on the website
    such as publishing fields.
    """

    DRAFT = 1
    PUBLISHED = 2
    HIDDEN = 3
    PUBLISH_CHOICES = (
        (DRAFT, _('Draft')),
        (PUBLISHED, _('Published')),
        (HIDDEN, _('Hidden')),
    )

    publish_status = models.SmallIntegerField(
            choices=PUBLISH_CHOICES,
            default=PUBLISHED,
            db_index=True,
            verbose_name=_('Status'))
    publish_from = models.DateTimeField(
            blank=True,
            default=timezone.now,
            null=True,
            verbose_name=_('Publish From'),
            help_text=_("Won't be shown until this time."))
    publish_to = models.DateTimeField(
            blank=True,
            null=True,
            verbose_name=_('To'),
            help_text=_("Won't be shown after this time."))

    objects = managers.DisplayableManager()
    search_fields = {'slug': 1}

    class Meta:
        abstract = True

    def clean(self):
        super(Displayable, self).clean()
        if (self.publish_from and self.publish_to
                and self.publish_to < self.publish_from):
            msg = _('End date cannot be earlier than starting date.')
            raise ValidationError({'publish_to': msg})

    def get_default_meta_index(self):
        if self.is_published():
            return super(Displayable, self).get_default_meta_index()
        else:
            return False

    def is_draft(self):
        return (self.publish_status == Displayable.DRAFT)
    is_draft.boolean = True
    is_draft.short_description = _('Is Draft?')

    def is_hidden(self):
        return (self.publish_status == Displayable.HIDDEN)
    is_hidden.boolean = True
    is_hidden.short_description = _('Is Hidden?')

    def is_published(self, date=None):
        if self.publish_status != Displayable.PUBLISHED:
            return False

        if self.publish_from is None and self.publish_to is None:
            return True

        if date is None:
            date = timezone.now()

        return ((self.publish_from is None or self.publish_from <= date)
                and (self.publish_to is None or self.publish_to >= date))
    is_published.boolean = True
    is_published.short_description = _('Is Published?')

