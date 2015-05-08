# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from django.core.management.base import BaseCommand
from django.db import transaction

from yepes.loading import get_model, get_models
from yepes.model_mixins import Nestable


class Command(BaseCommand):
    help = ('Rebuilds the trees of nestable models. If no app label is passed, '
            'rebuilds all the trees. Otherwise, only rebuilds the trees found '
            'in this apps.')

    args = '<label label ...>'
    requires_model_validation = True

    def handle(self, *labels, **options):

        if not labels:
            models = get_models()
        else:
            models = []
            for label in labels:
                if '.' in label:
                    models.append(get_model(*label.rsplit('.', 1)))
                else:
                    models.extend(get_models(label))

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

            self.stdout.write('All trees were successfully regenerated.')
        else:
            self.stdout.write('No tree was found.')

