# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from django.core.management.base import BaseCommand, CommandError

from yepes.contrib.datamigrations.facades import SingleImportFacade


class Command(BaseCommand):
    help = 'Loads all entries from the given file to the specified model.'

    requires_system_checks = True

    def add_arguments(self, parser):
        parser.add_argument('args', metavar='app_label.ModelName', nargs='*')
        parser.add_argument('-f', '--file',
            action='store',
            default=None,
            dest='file',
            help='Specifies a file from which the data will be readed.')
        parser.add_argument('--format',
            action='store',
            default=None,
            dest='format',
            help='Specifies the serialization format of the imported data.')
        parser.add_argument('--encoding',
            action='store',
            default=None,
            dest='encoding',
            help='Specifies the encoding used to decode the imported data.')
        parser.add_argument('--newline',
            action='store',
            default=None,
            dest='newline',
            help='Specifies how the lines of the imported file end.')
        parser.add_argument('-p', '--plan',
            action='store',
            default='update_or_create',
            dest='plan',
            help='Specifies the importation plan used to import the data.')
        parser.add_argument('--batch',
            action='store',
            default=100,
            dest='batch',
            help='Maximum number of entries that can be imported at a time.',
            type=int)
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
        parser.add_argument('--natural',
            action='store_true',
            default=False,
            dest='natural',
            help=('Use natural keys if they are available (both primary and '
                  'foreign keys).'))
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
        parser.add_argument('-i', '--ignore-missing',
            action='store_true',
            default=False,
            dest='ignore_missing',
            help=('Ignore entries in the serialized data whose foreign '
                  'keys point to objects that do not currently exist in '
                  'the database.'))

    def handle(self, *labels, **options):
        verbosity = options['verbosity']
        show_traceback = options['traceback']

        file_path = options['file']
        if not file_path:
            raise CommandError('You must give an input file.')

        kwargs = {
            'serializer': options['format'],
            'encoding': options['encoding'],
            'newline': options['newline'],
            'plan': options['plan'],
            'batch_size': options['batch'],
            'use_natural_primary_keys': options['natural'] or options['natural_primary'],
            'use_natural_foreign_keys': options['natural'] or options['natural_foreign'],
            'ignore_missing_foreign_keys': options['ignore_missing'],
        }
        if labels:

            if len(labels) > 1:
                raise CommandError('This command takes only one positional argument.')

            if labels[0].count('.') != 1:
                raise CommandError("Model label must be like 'appname.ModelName'.")

            kwargs['model'] = labels[0]

        if options['fields'] is not None:
            kwargs['fields'] = options['fields'].split(',')

        if options['exclude'] is not None:
            kwargs['exclude'] = options['exclude'].split(',')

        try:

            SingleImportFacade.from_file_path(file_path, **kwargs)

        except Exception as e:
            if show_traceback:
                raise e
            else:
                raise CommandError(str(e))

        if verbosity >= 1:
            self.stdout.write('Entries were successfully imported.')

