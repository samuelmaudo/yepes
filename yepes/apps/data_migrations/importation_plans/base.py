# -*- coding:utf-8 -*-

from __future__ import unicode_literals

import collections
import operator

from django.db import transaction
from django.db.models import F, Q
from django.utils.six.moves import reduce

from yepes.apps.data_migrations.exceptions import (
    UnableToCreateError,
    UnableToUpdateError,
)
from yepes.utils.iterators import isplit


class ImportationPlan(object):
    """
    Base class for data-importation plan implementations.

    Subclasses must at least overwrite ``import_batch()``.

    """
    needs_create = False
    needs_update = False

    def __init__(self, migration):
        self.migration = migration

    def _get_existing_object_keys(self, batch):
        key = self.migration.primary_key
        if key is None:
            return set()

        qs = self._get_queryset_of_existing_objects(batch)
        if not isinstance(key, collections.Iterable):
            return set(qs.values_list(key.attname, flat=True).iterator())
        else:
            key_attrs = [k.attname for k in key]
            return set(qs.values_list(*key_attrs).iterator())

    def _get_existing_objects(self, batch):
        key = self.migration.primary_key
        if key is None:
            return {}

        qs = self._get_queryset_of_existing_objects(batch)
        if not isinstance(key, collections.Iterable):
            key_attr = key.attname
            return {
                getattr(obj, key_attr): obj
                for obj
                in qs.iterator()
            }
        else:
            key_attrs = [k.attname for k in key]
            return {
                tuple(getattr(obj, attr) for attr in key_attrs): obj
                for obj
                in qs.iterator()
            }

    def _get_queryset_of_existing_objects(self, batch):
        key = self.migration.primary_key
        model = self.migration.model
        manager = model._default_manager
        if key is None:
            return manager.none()

        if not isinstance(key, collections.Iterable):
            key_attr = key.attname
            return manager.filter(**{
                '{0}__in'.format(key_attr): (
                    row[key_attr]
                    for row
                    in batch
                )
            })
        else:
            key_attrs = [k.attname for k in key]
            return manager.filter(reduce(operator.or_, (
                Q(**{
                    attr: row[attr]
                    for attr
                    in key_attrs
                })
                for row
                in batch
            )))

    def check_conditions(self):
        if self.needs_create and not self.migration.can_create:
            raise UnableToCreateError
        if self.needs_update and not self.migration.can_update:
            raise UnableToUpdateError

    def import_batch(self, batch):
        raise NotImplementedError('Subclasses of ImportationPlan must override import_batch() method')

    def prepare_batch(self, batch):
        m = self.migration
        if m.natural_foreign_keys is not None:
            for fld in m.natural_foreign_keys:
                attr = fld.attname
                path = fld.path
                rel_field = m.model_fields[fld][-1]
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
                    ).iterator()
                )
                if not m.ignore_missing_foreign_keys:
                    for row in batch:
                        row[attr] = keys[row.pop(path)]
                else:
                    erroneous_rows = []
                    for i, row in enumerate(batch):
                        try:
                            value = keys[row.pop(path)]
                        except KeyError:
                            erroneous_rows.append(i)
                        else:
                            row[attr] = value

                    for i in reversed(erroneous_rows):
                        del batch[i]

        return batch

    def prepare_importation(self):
        pass

    def run(self, data, batch_size=100):
        self.check_conditions()
        with transaction.atomic():
            self.prepare_importation()
            for batch in isplit(data, batch_size):
                self.import_batch(self.prepare_batch(batch))

