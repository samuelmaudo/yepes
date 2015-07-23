# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from django.utils import six

from yepes.conf import settings
from yepes.loading import get_module, LoadingError

BUILTIN_PLANS = {
    'bulk_create': 'yepes.data_migrations.importation_plans.bulk_create.BulkCreatePlan',
    'create': 'yepes.data_migrations.importation_plans.create.CreatePlan',
    'direct': 'yepes.data_migrations.importation_plans.direct.DirectPlan',
    'update': 'yepes.data_migrations.importation_plans.update.UpdatePlan',
    'update_or_bulk_create': 'yepes.data_migrations.importation_plans.update_or_bulk_create.UpdateOrBulkCreatePlan',
    'update_or_create': 'yepes.data_migrations.importation_plans.update_or_create.UpdateOrCreatePlan',
}

_PLANS = None


class MissingPlanError(LoadingError):

    def __init__(self, plan_name):
        msg = "Importation plan '{0}' could not be found."
        super(MissingPlanError, self).__init__(msg.format(plan_name))


def get_plan(name):
    if not has_plan(name):
        raise MissingPlanError(name)
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
    module = get_module(module_path, ignore_internal_errors=True)
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

