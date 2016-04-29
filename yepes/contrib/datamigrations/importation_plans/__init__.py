# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from django.utils import six

from yepes.conf import settings
from yepes.utils.modules import import_module

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

_PLANS = None


MissingPlanError = LookupError


def get_plan(name):
    if not has_plan(name):
        msg = "Importation plan '{0}' could not be found."
        raise LookupError(msg.format(name))
    else:
        return _PLANS[name]


def has_plan(name):
    if _PLANS is None:
        _load_plans()
    return (name in _PLANS)


def register_plan(name, path):
    if _PLANS is None:
        _load_plans()
    plan_class = _import_plan(path)
    if plan_class is not None:
        _PLANS[name] = plan_class


def _import_plan(path):
    module_path, class_name = path.rsplit('.', 1)
    module = import_module(module_path, ignore_internal_errors=True)
    return getattr(module, class_name, None)


def _load_plans():
    global _PLANS
    plans = {}

    for name, path in six.iteritems(BUILTIN_PLANS):
        plan_class = _import_plan(path)
        if plan_class is not None:
            plans[name] = plan_class

    if hasattr(settings, 'IMPORTATION_PLANS'):
        for name, path in six.iteritems(settings.IMPORTATION_PLANS):
            plan_class = _import_plan(path)
            if plan_class is not None:
                plans[name] = plan_class

    _PLANS = plans

