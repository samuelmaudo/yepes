# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from django.core.management.base import BaseCommand, CommandError
from django.utils import six

from yepes.contrib.datamigrations.facades import SingleExportFacade


class Command(BaseCommand):
    help = 'Dumps all objects of the specified model.'

    requires_system_checks = True

    def add_arguments(self, parser):
        parser.add_argument('args', metavar='app_label.ModelName', nargs='*')
        parser.add_argument('--all',
            action='store_true',
            default=False,
            dest='base_manager',
            help="Use Django's base manager to dump all models stored in the database.")
        parser.add_argument('-f', '--file',
            action='store',
            default=None,
            dest='file',
            help='Specifies a file to write the serialized data to.')
        parser.add_argument('--format',
            action='store',
            default=None,
            dest='format',
            help='Specifies the serialization format of the output.')
        parser.add_argument('--encoding',
            action='store',
            default=None,
            dest='encoding',
            help='Specifies the encoding used to encode the output.')
        parser.add_argument('--newline',
            action='store',
            default=None,
            dest='newline',
            help='Specifies how to end lines.')
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

    def handle(self, *labels, **options):
        verbosity = options['verbosity']
        show_traceback = options['traceback']

        file_path = options['file']

        kwargs = {
            'serializer': options['format'],
            'encoding': options['encoding'],
            'newline': options['newline'],
            'use_natural_primary_keys': options['natural'] or options['natural_primary'],
            'use_natural_foreign_keys': options['natural'] or options['natural_foreign'],
            'use_base_manager': options['base_manager'],
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

            if file_path:
                SingleExportFacade.to_file_path(file_path, **kwargs)
            else:
                file = self.stdout
                if six.PY2:

                    class FileWrapper(object):
                        def __init__(self, file, encoding, errors):
                            self._file = file
                            self._encoding = encoding
                            self._errors = errors
                        def __getattr__(self, name):
                            return getattr(self._file, name)
                        def write(self, data):
                            self._file.write(data.decode(
                                    self._encoding,
                                    self._errors))
                        def writelines(self, data):
                            for line in data:
                                self.write(line)

                    file = FileWrapper(file, 'utf8', 'replace')

                SingleExportFacade.to_file(file, **kwargs)

        except Exception as e:
            if show_traceback:
                raise e
            else:
                raise CommandError(str(e))

        if verbosity >= 1 and file_path:
            self.stdout.write('Objects were successfully exported.')

