# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from optparse import make_option

from django.core.management.base import NoArgsCommand, CommandError

from yepes.contrib.slugs import SlugHistory


class Command(NoArgsCommand):
    help = 'Populates the slug history.'
    option_list = NoArgsCommand.option_list + (
        make_option('-f', '--force',
            action='store_true',
            default=False,
            dest='force',
            help='Collects slugs even if the history is not empty.'),
        make_option('-a', '--app-label',
            action='store',
            dest='app_label',
            help='Limits the slug collection to the models of the given application.'),
        make_option('-m', '--model-names',
            action='store',
            dest='model_names',
            help='Limits the slug collection to the given models.'),
    )
    requires_model_validation = True

    def handle_noargs(self, **options):
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

