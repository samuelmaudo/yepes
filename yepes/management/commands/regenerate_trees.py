# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from django.core.management.base import BaseCommand
from django.db import transaction

from yepes.apps import apps
from yepes.model_mixins import Nestable


class Command(BaseCommand):
    help = ('Rebuilds the trees of nestable models. If no app label is passed, '
            'rebuilds all the trees. Otherwise, only rebuilds the trees found '
            'in this apps.')

    requires_system_checks = True

    def add_arguments(self, parser):
        parser.add_argument('args', metavar='app_label[.ModelName]', nargs='*')

    def handle(self, *labels, **options):
        if not labels:
            models = apps.get_models()
        else:
            models = []
            for label in labels:
                if '.' in label:
                    models.append(apps.get_model(label))
                else:
                    models.extend(apps.get_app_config(label).get_models())

        nested_models = [
            model
            for model
            in models
            if issubclass(model, Nestable)
        ]
        if nested_models:
            for model in nested_models:
                self.stdout.write('Regenerating {0}.{1} ...'.format(
                    model._meta.app_label,
                    model.__name__,
                ))
                with transaction.atomic():
                    model._tree_manager.rebuild()

            self.stdout.write('Trees were successfully regenerated.')
        else:
            self.stdout.write('No tree was found.')

