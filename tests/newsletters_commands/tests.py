# -*- coding:utf-8 -*-

from __future__ import unicode_literals

import os

from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase
from django.utils._os import upath
from django.utils.six import StringIO

from yepes.contrib.newsletters.models import Domain, Subscriber, SubscriberTag
from yepes.test_mixins import TempDirMixin

MODULE_DIR = os.path.abspath(os.path.dirname(upath(__file__)))
MIGRATIONS_DIR = os.path.join(MODULE_DIR, 'data_migrations')


class ImportSubscribersTest(TempDirMixin, TestCase):

    maxDiff = None
    tempDirPrefix = 'test_newsletters_commands_'

    def test_arguments(self):
        with self.assertRaisesRegexp(CommandError, "Command doesn't accept any arguments"):
            call_command('import_subscribers', 'argument')

    def test_no_file(self):
        with self.assertRaisesRegexp(CommandError, 'You must give an input file.'):
            call_command('import_subscribers')

    def test_file_not_found(self):
        with self.assertRaisesRegexp(CommandError, "File 'filename' does not exit."):
            call_command('import_subscribers', input='filename')

    def test_serializer_not_found(self):
        source_path = os.path.join(MIGRATIONS_DIR, 'subscribers.csv')
        with self.assertRaisesRegexp(CommandError, "Serializer 'serializername' could not be found."):
            call_command('import_subscribers', input=source_path, format='serializername')

    def test_file(self):
        source_path = os.path.join(MIGRATIONS_DIR, 'subscribers.csv')
        with open(source_path, 'r') as source_file:
            source = source_file.read()

        output = StringIO()
        call_command(
            'import_subscribers',
            format='csv',
            input=source_path,
            stdout=output,
        )
        self.assertIn('Subscribers were successfully imported.', output.getvalue())
        self.assertEqual(1, Domain.objects.count())
        self.assertEqual(3, Subscriber.objects.count())
        self.assertEqual(2, SubscriberTag.objects.count())

