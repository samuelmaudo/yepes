# -*- coding:utf-8 -*-

from __future__ import unicode_literals

import os
from optparse import make_option

from django.core.management.base import CommandError, NoArgsCommand

from yepes.apps import apps
from yepes.contrib.datamigrations.serializers import serializers

SubscriberImportation = apps.get_class('newsletters.migrations', 'SubscriberImportation')


class Command(NoArgsCommand):
    help = 'Loads all subscribers from the given file.'

    option_list = NoArgsCommand.option_list + (
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
        make_option('--batch',
            action='store',
            default=100,
            dest='batch',
            help='Maximum number of messages that can be dispatched.',
            type='int'),
    )
    requires_model_validation = True

    def handle_noargs(self, **options):
        serializer_name = options['format']
        file_path = options['input']
        batch_size = options['batch']

        if not file_path:
            raise CommandError('You must give an input file.')
        elif not os.path.exists(file_path):
            raise CommandError("File '{0}' does not exit.".format(file_path))

        try:
            serializer = serializers.get_serializer(serializer_name)
        except LookupError as e:
            raise CommandError(str(e))

        migration = SubscriberImportation()
        with open(file_path, 'r') as file:
            migration.import_data(file, serializer, None, batch_size)

        self.stdout.write('Subscribers were successfully imported.')

