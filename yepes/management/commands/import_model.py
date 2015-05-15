# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from optparse import make_option

from django.core.management.base import BaseCommand, CommandError

from yepes.data_migrations import DataMigration
from yepes.data_migrations.importation_plans import get_plan
from yepes.data_migrations.serializers import get_serializer
from yepes.exceptions import LoadingError
from yepes.loading import get_model


class Command(BaseCommand):
    help = ('Loads all objects from the given file in the specified model.')

    args = '<appname.ModelName>'
    option_list = BaseCommand.option_list + (
        make_option('-i', '--input',
            action='store',
            default=None,
            dest='input',
            help='Specifies the file from which the data is read.'),
        make_option('-f', '--format',
            action='store',
            default='json',
            dest='format',
            help='Specifies the serialization format of imported data.'),
        make_option('-p', '--plan',
            action='store',
            default='update_or_create',
            dest='plan',
            help='Specifies the importation plan used to import data.'),
        make_option('--batch',
            action='store',
            default=100,
            dest='batch',
            help='Maximum number of messages that can be dispatched.',
            type='int'),
        make_option('--fields',
            action='store',
            default=None,
            dest='fields',
            help='A list of field names to use in the migration.'),
        make_option('--exclude',
            action='store',
            default=None,
            dest='exclude',
            help='A list of field names to exclude from the migration.'),
        make_option('--natural-primary',
            action='store_true',
            default=False,
            dest='natural_primary',
            help='Use natural primary keys if they are available.'),
        make_option('--natural-foreign',
            action='store_true',
            default=False,
            dest='natural_foreign',
            help='Use natural foreign keys if they are available.'),
    )
    requires_model_validation = True

    def handle(self, *labels, **options):
        if len(labels) != 1:
            raise CommandError('This command takes one and only one positional argument.')

        model_name = labels[0]
        fields = options['fields'].split(',') if options['fields'] else None
        exclude = options['exclude'].split(',') if options['exclude'] else None
        use_natural_primary_keys = options['natural_primary']
        use_natural_foreign_keys = options['natural_foreign']
        serializer_name = options['format']
        plan_name = options['plan']
        file_path = options['input']
        batch_size = options['batch']

        if '.' not in model_name:
            raise CommandError("Model label must be like 'appname.ModelName'.")

        if not file_path:
            raise CommandError("You must give an input file.")

        try:
            model = get_model(*model_name.rsplit('.', 1))
        except LoadingError as e:
            raise CommandError(str(e))

        try:
            serializer = get_serializer(serializer_name)
        except LoadingError as e:
            raise CommandError(str(e))

        try:
            plan = get_plan(plan_name)
        except LoadingError as e:
            raise CommandError(str(e))

        migration = DataMigration(
            model,
            fields,
            exclude,
            use_natural_primary_keys,
            use_natural_foreign_keys,
        )
        with open(file_path, 'rb') as file:
            migration.import_data(file, serializer, plan, batch_size)

        self.stdout.write('Objects were successfully imported.')

