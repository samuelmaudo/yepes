# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from yepes.contrib.datamigrations.importation_plans import ModelImportationPlan


class DirectPlan(ModelImportationPlan):

    updates_data = False

    def import_batch(self, batch):
        model = self.migration.model
        manager = model._base_manager
        manager.bulk_create(
            model(**row)
            for row
            in batch
        )

