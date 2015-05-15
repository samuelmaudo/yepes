# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from yepes.data_migrations.importation_plans.base import ImportationPlan


class DirectPlan(ImportationPlan):

    needs_create = True

    def run(self, batch):
        model = self.migration.model
        model._default_manager.bulk_create(
            model(**row)
            for row
            in batch
        )

