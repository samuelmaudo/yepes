# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from django import VERSION as DJANGO_VERSION
from django.core.exceptions import ImproperlyConfigured
from django.db import models
if DJANGO_VERSION < (1, 9):
    from django.db.models.fields.related import ReverseSingleRelatedObjectDescriptor
else:
    from django.db.models.fields.related import ForwardManyToOneDescriptor as ReverseSingleRelatedObjectDescriptor

from yepes.utils.properties import cached_property


class CachedForeignKey(models.ForeignKey):

    def contribute_to_class(self, cls, name, **kwargs):
        super(CachedForeignKey, self).contribute_to_class(cls, name, **kwargs)
        setattr(cls, self.name, CachedRelatedObjectDescriptor(self))

    def deconstruct(self):
        name, path, args, kwargs = super(CachedForeignKey, self).deconstruct()
        path = path.replace('yepes.fields.cached_foreign_key', 'yepes.fields')
        return name, path, args, kwargs

    def get_default(self):
        if self.has_default():
            default = self.remote_field.model.cache.get_default()
            return getattr(default, self.target_field.attname, None)
        else:
            return None

    def has_default(self):
        if self.null:
            return False

        try:
            lookup_table = self.remote_field.model.cache
        except AttributeError:
            # Models do not have any lookup table during migrations.
            return False
        else:
            return lookup_table.has_default()


class CachedRelatedObjectDescriptor(ReverseSingleRelatedObjectDescriptor):

    @cached_property
    def RelatedObjectDoesNotExist(self):
        # The exception can't be created at initialization time since the
        # related model might not be resolved yet; `remote_field.model` might still be
        # a string model reference.
        return type(
            str('RelatedObjectDoesNotExist'),
            (self.field.remote_field.model.DoesNotExist, AttributeError),
            {},
        )

    @cached_property
    def related_lookup_table(self):
        model = self.field.remote_field.model
        try:
            lookup_table = model.cache
        except AttributeError:
            # Models do not have any lookup table during migrations.
            return model._default_manager
        else:
            return lookup_table

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
            if rel_obj is None or rel_id != rel_obj._get_pk_val():
                rel_obj = self.related_lookup_table.get(pk=rel_id)
                setattr(instance, self.cache_name, rel_obj)

        if rel_obj is None and not self.field.null:
            msg = '{0} has no {1}.'.format(
                self.field.model.__name__,
                self.field.name,
            )
            raise self.RelatedObjectDoesNotExist(msg)

        return rel_obj

