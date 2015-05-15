# -*- coding:utf-8 -*-

from __future__ import unicode_literals

import collections
import operator

from django.db.models import F, Q
from django.utils.six.moves import reduce

from yepes.data_migrations.exceptions import (
    UnableToCreateError,
    UnableToUpdateError,
)

class ImportationPlan(object):
    """
    Base class for data-importation plan implementations.

    Subclasses must at least overwrite ``run()``.

    """
    needs_create = False
    needs_update = False

    def __init__(self, migration):
        self.migration = migration

    def _get_existing_object_keys(self, batch):
        key = self.migration.primary_key
        if key is None:
            return set()

        manager = self.migration.model._default_manager
        if not isinstance(key, collections.Iterable):
            key_attr = key.attname
            return set(
                manager.filter(**{
                    '{0}__in'.format(key_attr): (
                        row[key_attr]
                        for row
                        in batch
                    )
                }).values_list(
                    key_attr,
                    flat=True,
                )
            )
        else:
            key_attrs = [k.attname for k in key]
            return set(
                manager.filter(reduce(operator.or_, (
                    Q(**{
                        attr: row[attr]
                        for attr
                        in key_attrs
                    })
                    for row
                    in batch
                ))).values_list(*key_attrs)
            )

    def _get_existing_objects(self, batch):
        key = self.migration.primary_key
        if key is None:
            return {}

        manager = self.migration.model._default_manager
        if not isinstance(key, collections.Iterable):
            key_attr = key.attname
            return {
                getattr(obj, key_attr): obj
                for obj
                in manager.filter(**{
                    '{0}__in'.format(key_attr): (
                        row[key_attr]
                        for row
                        in batch
                    )
                })
            }
        else:
            key_attrs = [k.attname for k in key]
            return {
                tuple(getattr(obj, attr) for attr in key_attrs): obj
                for obj
                in manager.filter(reduce(operator.or_, (
                    Q(**{
                        attr: row[attr]
                        for attr
                        in key_attrs
                    })
                    for row
                    in batch
                )))
            }

    def check(self):
        if self.needs_create and not self.migration.can_create:
            raise UnableToCreateError
        if self.needs_update and not self.migration.can_update:
            raise UnableToUpdateError

    def prepare(self, batch):
        if self.migration.natural_foreign_keys is not None:
            for fld in self.migration.natural_foreign_keys:
                attr = fld.attname
                path = fld.path
                rel_field = self.migration.model_fields[fld][-1]
                rel_manager = rel_field.model._default_manager
                keys = dict(
                    rel_manager.filter(**{
                        '{0}__in'.format(rel_field.name): {
                            row[path]
                            for row
                            in batch
                        }
                    }).values_list(
                        rel_field.name,
                        'pk',
                    )
                )
                for row in batch:
                    row[attr] = keys[row.pop(path)]

        return batch

    def run(self, batch):
        raise NotImplemented('subclasses of ImportationPlan must override run() method')

