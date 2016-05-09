# -*- coding:utf-8 -*-

from __future__ import unicode_literals

import collections

from django.utils import six

from yepes.contrib.datamigrations.importation_plans import ImportationPlan


class UpdateOrCreatePlan(ImportationPlan):

    needs_create = True
    needs_update = True

    def import_batch(self, batch):
        model = self.migration.model
        objs = self._get_existing_objects(batch)
        if not objs:
            for row in batch:
                model(**row).save(force_insert=True)
        else:
            key = self.migration.primary_key
            if not isinstance(key, collections.Iterable):
                key_attr = key.attname
                for row in batch:
                    obj = objs.get(row[key_attr])
                    if obj is not None:
                        for k, v in six.iteritems(row):
                            setattr(obj, k, v)
                        obj.save(force_update=True)
                    else:
                        model(**row).save(force_insert=True)
            else:
                key_attrs = [k.attname for k in key]
                for row in batch:
                    obj = objs.get(tuple(row[attr] for attr in key_attrs))
                    if obj is not None:
                        for k, v in six.iteritems(row):
                            setattr(obj, k, v)
                        obj.save(force_update=True)
                    else:
                        model(**row).save(force_insert=True)

