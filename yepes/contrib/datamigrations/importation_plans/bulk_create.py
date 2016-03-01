# -*- coding:utf-8 -*-

from __future__ import unicode_literals

import collections

from yepes.contrib.datamigrations.importation_plans.base import ImportationPlan


class BulkCreatePlan(ImportationPlan):

    needs_create = True

    def import_batch(self, batch):
        model = self.migration.model
        manager = model._default_manager
        obj_keys = self._get_existing_object_keys(batch)
        if not obj_keys:
            manager.bulk_create(
                model(**row)
                for row
                in batch
            )
        else:
            key = self.migration.primary_key
            if not isinstance(key, collections.Iterable):
                key_attr = key.attname
                manager.bulk_create(
                    model(**row)
                    for row
                    in batch
                    if row[key_attr] not in obj_keys
                )
            else:
                key_attrs = [k.attname for k in key]
                manager.bulk_create(
                    model(**row)
                    for row
                    in batch
                    if tuple(row[attr] for attr in key_attrs) not in obj_keys
                )

