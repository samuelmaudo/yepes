# -*- coding:utf-8 -*-

from __future__ import unicode_literals

import collections

from django.utils import six

from yepes.data_migrations.importation_plans.base import ImportationPlan


class UpdatePlan(ImportationPlan):

    needs_update = True

    def run(self, batch):
        objs = self._get_existing_objects(batch)
        if objs:
            model = self.migration.model
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
                key_attrs = [k.attname for k in key]
                for row in batch:
                    obj = objs.get(tuple(row[attr] for attr in key_attrs))
                    if obj is not None:
                        for k, v in six.iteritems(row):
                            setattr(obj, k, v)
                        obj.save(force_update=True)

