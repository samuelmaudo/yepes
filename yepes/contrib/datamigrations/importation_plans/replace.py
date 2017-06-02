# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from yepes.contrib.datamigrations.importation_plans import ModelImportationPlan


class ReplacePlan(ModelImportationPlan):

    needs_create = True
    needs_update = True

    def import_batch(self, batch):
        self.get_existing_queryset(batch).delete()
        model = self.migration.model
        manager = model._base_manager
        manager.bulk_create(
            model(**row)
            for row
            in batch
        )

