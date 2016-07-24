# -*- coding:utf-8 -*-

from __future__ import unicode_literals

import os

from django.core.management.base import BaseCommand, CommandError

from yepes.apps import apps
from yepes.contrib.datamigrations import DataMigration
from yepes.contrib.datamigrations.importation_plans import importation_plans
from yepes.contrib.datamigrations.serializers import serializers


class Command(BaseCommand):
    help = 'Loads all entries from the given file to the specified model.'

    requires_system_checks = True

    def add_arguments(self, parser):
        parser.add_argument('args', metavar='app_label.ModelName', nargs='*')
        parser.add_argument('-i', '--input',
            action='store',
            default=None,
            dest='input',
            help='Specifies the file from which the data is read.')
        parser.add_argument('-f', '--format',
            action='store',
            default='json',
            dest='format',
            help='Specifies the serialization format of imported data.')
        parser.add_argument('-p', '--plan',
            action='store',
            default='update_or_create',
            dest='plan',
            help='Specifies the importation plan used to import data.')
        parser.add_argument('--batch',
            action='store',
            default=100,
            dest='batch',
            help='Maximum number of messages that can be dispatched.',
            type=int),
        parser.add_argument('--fields',
            action='store',
            default=None,
            dest='fields',
            help='A list of field names to use in the migration.')
        parser.add_argument('--exclude',
            action='store',
            default=None,
            dest='exclude',
            help='A list of field names to exclude from the migration.')
        parser.add_argument('--natural-primary',
            action='store_true',
            default=False,
            dest='natural_primary',
            help='Use natural primary keys if they are available.')
        parser.add_argument('--natural-foreign',
            action='store_true',
            default=False,
            dest='natural_foreign',
            help='Use natural foreign keys if they are available.')
        parser.add_argument('--ignore-missing-keys',
            action='store_true',
            default=False,
            dest='ignore_missing_keys',
            help=('Ignores entries in the serialized data whose foreign '
                  'keys point to objects that do not currently exist in '
                  'the database.'))

    def handle(self, *labels, **options):
        if len(labels) != 1:
            raise CommandError('This command takes one and only one positional argument.')

        model_name = labels[0]
        fields = options['fields'].split(',') if options['fields'] else None
        exclude = options['exclude'].split(',') if options['exclude'] else None
        use_natural_primary_keys = options['natural_primary']
        use_natural_foreign_keys = options['natural_foreign']
        ignore_missing_foreign_keys = options['ignore_missing_keys']
        serializer_name = options['format']
        plan_name = options['plan']
        file_path = options['input']
        batch_size = options['batch']

        if '.' not in model_name:
            raise CommandError("Model label must be like 'appname.ModelName'.")

        if not file_path:
            raise CommandError('You must give an input file.')
        elif not os.path.exists(file_path):
            raise CommandError("File '{0}' does not exit.".format(file_path))

        try:
            model = apps.get_model(model_name)
        except LookupError as e:
            raise CommandError(str(e))

        try:
            serializer = serializers.get_serializer(serializer_name)
        except LookupError as e:
            raise CommandError(str(e))

        try:
            plan = importation_plans.get_plan(plan_name)
        except LookupError as e:
            raise CommandError(str(e))

        migration = DataMigration(
            model,
            fields,
            exclude,
            use_natural_primary_keys,
            use_natural_foreign_keys,
            ignore_missing_foreign_keys,
        )
        with open(file_path, 'r') as file:
            migration.import_data(file, serializer, plan, batch_size)

        self.stdout.write('Entries were successfully imported.')

