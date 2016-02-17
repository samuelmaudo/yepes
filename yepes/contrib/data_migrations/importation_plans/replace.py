# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from yepes.contrib.data_migrations.importation_plans.base import ImportationPlan


class ReplacePlan(ImportationPlan):

    needs_create = True
    needs_update = True

    def import_batch(self, batch):
        self._get_queryset_of_existing_objects(batch).delete()
        model = self.migration.model
        manager = model._default_manager
        manager.bulk_create(
            model(**row)
            for row
            in batch
        )

