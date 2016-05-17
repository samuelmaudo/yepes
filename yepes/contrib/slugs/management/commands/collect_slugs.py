# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from django.core.management.base import BaseCommand, CommandError

from yepes.contrib.slugs import SlugHistory


class Command(BaseCommand):
    help = 'Populates the slug history.'

    requires_system_checks = True

    def add_arguments(self, parser):
        parser.add_argument('-f', '--force',
            action='store_true',
            default=False,
            dest='force',
            help='Collects slugs even if the history is not empty.')
        parser.add_argument('-a', '--app-label',
            action='store',
            dest='app_label',
            help='Limits the slug collection to the models of the given application.')
        parser.add_argument('-m', '--model-names',
            action='store',
            dest='model_names',
            help='Limits the slug collection to the given models.')

    def handle(self, **options):
        force = options.get('force')

        app_label = options.get('app_label')
        if not app_label:
            app_label = None

        model_names = options.get('model_names')
        if not model_names:
            model_names = None
        else:
            model_names = model_names.split(',')

        SlugHistory.objects.populate(
                force=force,
                app_label=app_label,
                model_names=model_names)

        verbosity = int(options.get('verbosity', '1'))
        if verbosity > 0:
            self.stdout.write('Slugs were successfully collected.')

