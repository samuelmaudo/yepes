# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from django.contrib.contenttypes.fields import GenericRelation
from django.utils.translation import ugettext_lazy as _

from yepes import fields
from yepes import managers
from yepes.apps import apps
from yepes.model_mixins import Linked


class Slugged(Linked):
    """
    Abstract model that handles auto-generating slugs. Inherits from `Linked`.
    """

    slug = fields.SlugField(
            max_length=63,
            unique=True,
            verbose_name=_('Slug'),
            help_text=_('URL friendly version of the main title. '
                        'It is usually all lowercase and contains only '
                        'letters, numbers and hyphens.'))

    if 'slugs' in apps:
        slug_history = GenericRelation(
                'slugs.SlugHistory',
                content_type_field='object_type',
                object_id_field='object_id',
                verbose_name=_('Slug History'))

    objects = managers.SluggedManager()

    class Meta:
        abstract = True

    def __init__(self, *args, **kwargs):
        super(Slugged, self).__init__(*args, **kwargs)
        self.old_slug = self.slug

    def natural_key(self):
        return (self.slug, )

    def save(self, **kwargs):
        updated_fields = kwargs.get('update_fields', False)
        new_record = (kwargs.get('force_insert', False)
                        or not (self._get_pk_val() or updated_fields))

        super(Slugged, self).save(**kwargs)
        if ('slugs' in apps
                and (new_record
                        or (self.slug != self.old_slug
                                and (not updated_fields
                                        or 'slug' in updated_fields)))):
            self.slug_history.create(slug=self.slug)
            self.old_slug = self.slug

