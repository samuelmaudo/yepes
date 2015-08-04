# -*- coding:utf-8 -*-

from __future__ import unicode_literals

import hashlib
import os

from django.test import TestCase

from yepes.apps.thumbnails.models import Configuration
from yepes.apps.thumbnails.proxies import ConfigurationProxy
from yepes.apps.thumbnails.test_mixins import ThumbnailsMixin


class ThumbnailsTest(ThumbnailsMixin, TestCase):

    tempDirPrefix = 'test_thumbnails_'

    def test_simple_configuration(self):
        configuration = Configuration.objects.create(
            key='default',
            width=100,
            height=50,
        )
        salt = os.path.join(configuration.key, self.source.name)
        salt = hashlib.md5(salt).hexdigest()[:6]
        path = os.path.join(
            self.temp_dir,
            'thumbs',
            'wolf_{0}.jpg'.format(salt),
        )
        self.assertIsNone(self.source.get_existing_thumbnail('default'))

        thumbnail = self.source.get_thumbnail('default')
        self.assertEqual(thumbnail.path, path)
        self.assertLessEqual(thumbnail.width, 100)
        self.assertLessEqual(thumbnail.height, 50)
        self.assertEqual(thumbnail.format, 'JPEG')
        original_accessed_time = thumbnail.accessed_time
        original_created_time = thumbnail.created_time
        original_modified_time = thumbnail.modified_time
        original_size = thumbnail.size

        thumbnail = self.source.get_existing_thumbnail('default')
        self.assertEqual(thumbnail.path, path)
        self.assertLessEqual(thumbnail.width, 100)
        self.assertLessEqual(thumbnail.height, 50)
        self.assertEqual(thumbnail.format, 'JPEG')
        self.assertNotEqual(thumbnail.accessed_time, original_accessed_time)
        self.assertEqual(thumbnail.created_time, original_created_time)
        self.assertEqual(thumbnail.modified_time, original_modified_time)
        self.assertEqual(thumbnail.size, original_size)

        thumbnail = self.source.get_thumbnail('default')
        self.assertEqual(thumbnail.path, path)
        self.assertLessEqual(thumbnail.width, 100)
        self.assertLessEqual(thumbnail.height, 50)
        self.assertEqual(thumbnail.format, 'JPEG')
        self.assertNotEqual(thumbnail.accessed_time, original_accessed_time)
        self.assertEqual(thumbnail.created_time, original_created_time)
        self.assertEqual(thumbnail.modified_time, original_modified_time)
        self.assertEqual(thumbnail.size, original_size)

    def test_proxy_configuration(self):
        configuration = ConfigurationProxy(
            width=100,
            height=50,
        )
        self.assertEqual(configuration.key, 'w100_h50')
        salt = os.path.join(configuration.key, self.source.name)
        salt = hashlib.md5(salt).hexdigest()[:6]
        path = os.path.join(
            self.temp_dir,
            'thumbs',
            'wolf_{0}.jpg'.format(salt),
        )
        self.assertIsNone(self.source.get_existing_thumbnail(configuration))

        thumbnail = self.source.get_thumbnail(configuration)
        self.assertEqual(thumbnail.path, path)
        self.assertLessEqual(thumbnail.width, configuration.width)
        self.assertLessEqual(thumbnail.height, configuration.height)
        self.assertEqual(thumbnail.format, 'JPEG')
        original_accessed_time = thumbnail.accessed_time
        original_created_time = thumbnail.created_time
        original_modified_time = thumbnail.modified_time
        original_size = thumbnail.size

        thumbnail = self.source.get_existing_thumbnail(configuration)
        self.assertEqual(thumbnail.path, path)
        self.assertLessEqual(thumbnail.width, configuration.width)
        self.assertLessEqual(thumbnail.height, configuration.height)
        self.assertEqual(thumbnail.format, configuration.format)
        self.assertNotEqual(thumbnail.accessed_time, original_accessed_time)
        self.assertEqual(thumbnail.created_time, original_created_time)
        self.assertEqual(thumbnail.modified_time, original_modified_time)
        self.assertEqual(thumbnail.size, original_size)

        thumbnail = self.source.get_thumbnail(configuration)
        self.assertEqual(thumbnail.path, path)
        self.assertLessEqual(thumbnail.width, configuration.width)
        self.assertLessEqual(thumbnail.height, configuration.height)
        self.assertEqual(thumbnail.format, configuration.format)
        self.assertNotEqual(thumbnail.accessed_time, original_accessed_time)
        self.assertEqual(thumbnail.created_time, original_created_time)
        self.assertEqual(thumbnail.modified_time, original_modified_time)
        self.assertEqual(thumbnail.size, original_size)
