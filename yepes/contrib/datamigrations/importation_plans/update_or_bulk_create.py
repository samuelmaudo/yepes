# -*- coding:utf-8 -*-

from __future__ import unicode_literals

import collections

from django.utils import six

from yepes.contrib.datamigrations.importation_plans import ModelImportationPlan


class UpdateOrBulkCreatePlan(ModelImportationPlan):

    needs_create = True
    needs_update = True

    def import_batch(self, batch):
        model = self.migration.model
        manager = model._base_manager
        objs = self.get_existing_objects(batch)
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
                        is_modified = False
                        for k, v in six.iteritems(row):
                            if v != getattr(obj, k):
                                setattr(obj, k, v)
                                is_modified = True
                        if is_modified:
                            obj.save(force_update=True)
                    else:
                        new_objs.append(model(**row))
            else:
                key_attrs = [k.attname for k in key]
                for row in batch:
                    obj = objs.get(tuple(row[attr] for attr in key_attrs))
                    if obj is not None:
                        is_modified = False
                        for k, v in six.iteritems(row):
                            if v != getattr(obj, k):
                                setattr(obj, k, v)
                                is_modified = True
                        if is_modified:
                            obj.save(force_update=True)
                    else:
                        new_objs.append(model(**row))

            manager.bulk_create(new_objs)

