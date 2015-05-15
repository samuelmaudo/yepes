# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from optparse import make_option

from django.core.management.base import BaseCommand, CommandError

from yepes.data_migrations import DataMigration
from yepes.data_migrations.serializers import get_serializer
from yepes.exceptions import LoadingError
from yepes.loading import get_model


class Command(BaseCommand):
    help = ('Dumps all objects of the specified model.')

    args = '<appname.ModelName>'
    option_list = BaseCommand.option_list + (
        make_option('-o', '--output',
            action='store',
            default=None,
            dest='output',
            help='Specifies the file to which the data is written.'),
        make_option('-f', '--format',
            action='store',
            default='json',
            dest='format',
            help='Specifies the serialization format of exported data.'),
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
        file_path = options['output']

        if '.' not in model_name:
            raise CommandError("Model label must be like 'appname.ModelName'.")

        try:
            model = get_model(*model_name.rsplit('.', 1))
        except LoadingError as e:
            raise CommandError(str(e))

        try:
            serializer = get_serializer(serializer_name)
        except LoadingError as e:
            raise CommandError(str(e))

        migration = DataMigration(
            model,
            fields,
            exclude,
            use_natural_primary_keys,
            use_natural_foreign_keys,
        )
        if not file_path:
            data = migration.export_data(serializer=serializer)
            self.stdout.write(data.decode('utf8', 'replace'))
        else:
            with open(file_path, 'wb') as file:
                migration.export_data(file, serializer)
            self.stdout.write('Objects were successfully exported.')

