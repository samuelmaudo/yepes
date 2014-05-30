# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from django.core.exceptions import ImproperlyConfigured
from django.db import models
from django.db.models.fields.related import ReverseSingleRelatedObjectDescriptor
from django.utils.functional import cached_property


class CachedRelatedObjectDescriptor(ReverseSingleRelatedObjectDescriptor):

    @cached_property
    def RelatedObjectDoesNotExist(self):
        # The exception can't be created at initialization time since the
        # related model might not be resolved yet; `rel.to` might still be
        # a string model reference.
        return type(
            str('RelatedObjectDoesNotExist'),
            (self.field.rel.to.DoesNotExist, AttributeError),
            {},
        )

    @cached_property
    def related_lookup_table(self):
        return self.field.rel.to.cache

    def __get__(self, instance, instance_type=None):
        if instance is None:
            return self

        try:
            rel_obj = getattr(instance, self.cache_name)
        except AttributeError:
            values = self.field.get_local_related_value(instance)
            if None in values:
                rel_obj = None
            else:
                rel_obj = self.related_lookup_table.get(*values)

            setattr(instance, self.cache_name, rel_obj)

        if rel_obj is None and not self.field.null:
            try:
                rel_obj = self.related_lookup_table.get_default()
            except ImproperlyConfigured:
                msg = '{0} has no {1}.'.format(
                    self.field.model.__name__,
                    self.field.name,
                )
                raise self.RelatedObjectDoesNotExist(msg)

        return rel_obj


class CachedForeignKey(models.ForeignKey):

    def contribute_to_class(self, cls, name, virtual_only=False):
        super(CachedForeignKey, self).contribute_to_class(cls, name, virtual_only=virtual_only)
        setattr(cls, self.name, CachedRelatedObjectDescriptor(self))

    def get_default(self):
        try:
            default = self.rel.to.cache.get_default()
        except ImproperlyConfigured:
            return None
        else:
            return getattr(default, self.related_field.attname, None)

    def south_field_triple(self):
        """
        Returns a suitable description of this field for South.
        """
        from south.modelsinspector import introspector
        field_class = 'django.db.models.fields.ForeignKey'
        args, kwargs = introspector(self)
        return (field_class, args, kwargs)

