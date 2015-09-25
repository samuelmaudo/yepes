# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from yepes.apps.data_migrations.importation_plans.direct import DirectPlan


class ReplaceAllPlan(DirectPlan):

    def prepare_importation(self):
        model = self.migration.model
        manager = model._default_manager
        manager.truncate()

