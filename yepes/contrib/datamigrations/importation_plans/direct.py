# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from yepes.contrib.datamigrations.importation_plans import ImportationPlan


class DirectPlan(ImportationPlan):

    needs_create = True

    def import_batch(self, batch):
        model = self.migration.model
        manager = model._default_manager
        manager.bulk_create(
            model(**row)
            for row
            in batch
        )

