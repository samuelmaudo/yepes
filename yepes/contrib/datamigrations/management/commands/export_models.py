# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from django.core.management.base import BaseCommand, CommandError
from django.utils import six

from yepes.contrib.datamigrations.facades import MultipleExportFacade


class Command(BaseCommand):
    help = 'Dumps all objects of the specified models.'

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
        parser.add_argument('-d', '--directory',
            action='store',
            default=None,
            dest='directory',
            help='Specifies a directory to write the serialized data to.')
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
        parser.add_argument('--natural',
            action='store_true',
            default=False,
            dest='natural',
            help=('Use natural keys if they are available (both primary and '
                  'foreign keys).'))

    def handle(self, *labels, **options):
        verbosity = options['verbosity']
        show_traceback = options['traceback']

        file_path = options['file']
        directory = options['directory']
        if file_path and directory:
            raise CommandError('You must give either an output file or a directory.')

        kwargs = {
            'models': labels,
            'serializer': options['format'],
            'encoding': options['encoding'],
            'newline': options['newline'],
            'use_natural_keys': options['natural'],
            'use_base_manager': options['base_manager'],
        }
        try:

            if file_path:
                MultipleExportFacade.to_file_path(file_path, **kwargs)
            elif directory:
                MultipleExportFacade.to_directory(directory, **kwargs)
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

                MultipleExportFacade.to_file(file, **kwargs)

        except Exception as e:
            if show_traceback:
                raise e
            else:
                raise CommandError(str(e))

        if verbosity >= 1 and (file_path or directory):
            self.stdout.write('Objects were successfully exported.')

