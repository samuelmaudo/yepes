# -*- coding:utf-8 -*-

from __future__ import unicode_literals

import collections

from yepes.data_migrations.importation_plans.base import ImportationPlan


class CreatePlan(ImportationPlan):

    needs_create = True

    def run(self, batch):
        model = self.migration.model
        obj_keys = self._get_existing_object_keys(batch)
        if not obj_keys:
            for row in batch:
                model(**row).save(force_insert=True)
        else:
            key = self.migration.primary_key
            if not isinstance(key, collections.Iterable):
                key_attr = key.attname
                for row in batch:
                    if row[key_attr] not in obj_keys:
                        model(**row).save(force_insert=True)
            else:
                key_attrs = [k.attname for k in key]
                for row in batch:
                    if tuple(row[attr] for attr in key_attrs) not in obj_keys:
                        model(**row).save(force_insert=True)

