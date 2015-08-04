# -*- coding:utf-8 -*-

from __future__ import unicode_literals

import collections

from django.utils import six

from yepes.apps.data_migrations.importation_plans.base import ImportationPlan


class UpdateOrBulkCreatePlan(ImportationPlan):

    needs_create = True
    needs_update = True

    def run(self, batch):
        model = self.migration.model
        manager = model._default_manager
        objs = self._get_existing_objects(batch)
        if not objs:
            manager.bulk_create(
                model(**row)
                for row
                in batch
            )
        else:
            key = self.migration.primary_key
            new_objs = []
            if not isinstance(key, collections.Iterable):
                key_attr = key.attname
                for row in batch:
                    obj = objs.get(row[key_attr])
                    if obj is not None:
                        for k, v in six.iteritems(row):
                            setattr(obj, k, v)
                        obj.save(force_update=True)
                    else:
                        new_objs.append(model(**row))
            else:
                key_attrs = [k.attname for k in key]
                for row in batch:
                    obj = objs.get(tuple(row[attr] for attr in key_attrs))
                    if obj is not None:
                        for k, v in six.iteritems(row):
                            setattr(obj, k, v)
                        obj.save(force_update=True)
                    else:
                        new_objs.append(model(**row))

            manager.bulk_create(new_objs)

