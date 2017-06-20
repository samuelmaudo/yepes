# -*- coding:utf-8 -*-

from __future__ import unicode_literals

import os

from django.core.management.base import BaseCommand, CommandError

from yepes.apps import apps
from yepes.contrib.datamigrations.serializers import serializers

SubscriberImportation = apps.get_class('newsletters.data_migrations', 'SubscriberImportation')


class Command(BaseCommand):
    help = 'Loads all subscribers from the given file.'

    requires_system_checks = True

    def add_arguments(self, parser):
        parser.add_argument('-f', '--file',
            action='store',
            default=None,
            dest='file',
            help='Specifies a file from which the data will be readed.')
        parser.add_argument('--format',
            action='store',
            default=None,
            dest='format',
            help='Specifies the serialization format of the input.')
        parser.add_argument('--batch',
            action='store',
            default=100,
            dest='batch',
            help='Maximum number of entries that can be imported at a time.',
            type=int)

    def handle(self, **options):
        verbosity = options['verbosity']
        show_traceback = options['traceback']

        file_path = options['file']
        if not file_path:
            raise CommandError('You must give an input file.')
        elif not os.path.exists(file_path):
            raise CommandError("File '{0}' does not exit.".format(file_path))

        serializer_name = options['format']
        if serializer_name is None:
            _, file_ext = os.path.splitext(file_path)
            file_ext = file_ext.lstrip('.')
            if serializers.has_serializer(file_ext):
                serializer_name = file_ext

        try:

            migration = SubscriberImportation()
            serializer = migration.get_serializer(serializer_name)
            with serializer.open_to_load(file_path) as file:
                migration.import_data(file, serializer, None, options['batch'])

        except Exception as e:
            if show_traceback:
                raise e
            else:
                raise CommandError(str(e))

        if verbosity >= 1:
            self.stdout.write('Subscribers were successfully imported.')

