# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from django.utils import six

from yepes.conf import settings
from yepes.contrib.datamigrations.importation_plans.base import ImportationPlan, ModelImportationPlan
from yepes.utils.modules import import_module

__all__ = (
    'importation_plans',
    'get_plan', 'has_plan', 'register_plan',
    'ImportationPlan', 'ModelImportationPlan',
)

BUILTIN_PLANS = {
    'yepes.contrib.datamigrations.importation_plans.bulk_create.BulkCreatePlan',
    'yepes.contrib.datamigrations.importation_plans.create.CreatePlan',
    'yepes.contrib.datamigrations.importation_plans.direct.DirectPlan',
    'yepes.contrib.datamigrations.importation_plans.replace.ReplacePlan',
    'yepes.contrib.datamigrations.importation_plans.replace_all.ReplaceAllPlan',
    'yepes.contrib.datamigrations.importation_plans.update.UpdatePlan',
    'yepes.contrib.datamigrations.importation_plans.update_or_bulk_create.UpdateOrBulkCreatePlan',
    'yepes.contrib.datamigrations.importation_plans.update_or_create.UpdateOrCreatePlan',
}


class PlanRegistry(object):
    """
    A registry to retrieve Plan classes.
    """
    def __init__(self):
        self._registry = {}

    def __contains__(self, name):
        return name in self._registry

    def get_plan(self, name):
        if name not in self._registry:
            msg = "Importation plan '{0}' could not be found."
            raise LookupError(msg.format(name))
        else:
            return self._registry[name]

    def get_plans(self):
        return six.itervalues(self._registry)

    def has_plan(self, name):
        return name in self._registry

    def import_plan(self, path):
        module_path, class_name = path.rsplit('.', 1)
        module = import_module(module_path, ignore_internal_errors=True)
        return getattr(module, class_name, None)

    def register_plan(self, plan):
        if isinstance(plan, six.string_types):
            plan = self.import_plan(plan)

        if plan is not None:
            self._registry[plan.name] = plan
            return True
        else:
            return False

importation_plans = PlanRegistry()
for path in BUILTIN_PLANS:
    importation_plans.register_plan(path)
for path in settings.IMPORTATION_PLANS:
    importation_plans.register_plan(path)

get_plan = importation_plans.get_plan
has_plan = importation_plans.has_plan
register_plan = importation_plans.register_plan

