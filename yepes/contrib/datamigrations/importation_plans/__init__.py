# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from yepes.conf import settings
from yepes.contrib.datamigrations.importation_plans.base import ImportationPlan
from yepes.utils.modules import import_module

__all__ = (
    'MissingPlanError',
    'get_plan', 'has_plan', 'register_plan',
    'ImportationPlan',
    'importation_plans',
)

BUILTIN_PLANS = {
    'bulk_create': 'yepes.contrib.datamigrations.importation_plans.bulk_create.BulkCreatePlan',
    'create': 'yepes.contrib.datamigrations.importation_plans.create.CreatePlan',
    'direct': 'yepes.contrib.datamigrations.importation_plans.direct.DirectPlan',
    'replace': 'yepes.contrib.datamigrations.importation_plans.replace.ReplacePlan',
    'replace_all': 'yepes.contrib.datamigrations.importation_plans.replace_all.ReplaceAllPlan',
    'update': 'yepes.contrib.datamigrations.importation_plans.update.UpdatePlan',
    'update_or_bulk_create': 'yepes.contrib.datamigrations.importation_plans.update_or_bulk_create.UpdateOrBulkCreatePlan',
    'update_or_create': 'yepes.contrib.datamigrations.importation_plans.update_or_create.UpdateOrCreatePlan',
}

MissingPlanError = LookupError


class PlanHandler(object):
    """
    A Plan Handler to retrieve ImportationPlan classes.
    """
    def __init__(self):
        self._classes = {}
        self._registry =  {}
        self._registry.update(BUILTIN_PLANS)
        self._registry.update(getattr(settings, 'IMPORTATION_PLANS', []))

    def __contains__(self, name):
        return self.has_plan(name)

    def get_plan(self, name):
        try:
            return self._classes[name]
        except KeyError:
            pass

        if name not in self._registry:
            msg = "Importation plan '{0}' could not be found."
            raise LookupError(msg.format(name))

        plan = self.import_plan(self._registry[name])
        self._classes[name] = plan
        return plan

    def get_plans(self):
        return (self.__getitem__(name) for name in self._registry)

    def has_plan(self, name):
        return name in self._registry

    def import_plan(self, path):
        module_path, class_name = path.rsplit('.', 1)
        module = import_module(module_path, ignore_internal_errors=True)
        return getattr(module, class_name, None)

    def register_plan(self, name, path):
        self._registry[name] = path

importation_plans = PlanHandler()

get_plan = importation_plans.get_plan
has_plan = importation_plans.has_plan
register_plan = importation_plans.register_plan

