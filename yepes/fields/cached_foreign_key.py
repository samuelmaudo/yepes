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

        rel_id = getattr(instance, self.field.attname, None)
        rel_obj = getattr(instance, self.cache_name, None)
        if rel_id is None:
            if rel_obj is not None:
                rel_obj = None
                setattr(instance, self.cache_name, rel_obj)
        else:
            if rel_obj is None or rel_id != rel_obj.pk:
                rel_obj = self.related_lookup_table.get(rel_id)
                setattr(instance, self.cache_name, rel_obj)

        if rel_obj is None and not self.field.null:
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
        if self.has_default():
            default = self.rel.to.cache.get_default()
            return getattr(default, self.related_field.attname, None)
        else:
            return None

    def has_default(self):
        if not self.null:
            return self.rel.to.cache.has_default()
        else:
            return False

    def south_field_triple(self):
        """
        Returns a suitable description of this field for South.
        """
        from south.modelsinspector import introspector
        field_class = 'django.db.models.fields.ForeignKey'
        args, kwargs = introspector(self)
        return (field_class, args, kwargs)
