# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from base64 import b64encode
from hashlib import md5
import os

from django.test import TestCase
from django.utils.encoding import force_bytes

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
        key = '/'.join((configuration.key, 'wolf.jpg'))
        key = md5(force_bytes(key)).digest()
        key = b64encode(key, b'ab').decode('ascii')[:6]
        path = os.path.join(
            self.temp_dir,
            'thumbs',
            'wolf_{0}.jpg'.format(key),
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
        self.assertFalse(thumbnail.closed)

        thumbnail = self.source.get_existing_thumbnail('default')
        self.assertEqual(thumbnail.path, path)
        self.assertLessEqual(thumbnail.width, 100)
        self.assertLessEqual(thumbnail.height, 50)
        self.assertEqual(thumbnail.format, 'JPEG')
        self.assertGreaterEqual(thumbnail.accessed_time, original_accessed_time)
        self.assertEqual(thumbnail.created_time, original_created_time)
        self.assertEqual(thumbnail.modified_time, original_modified_time)
        self.assertEqual(thumbnail.size, original_size)
        self.assertTrue(thumbnail.closed)

        thumbnail = self.source.get_thumbnail('default')
        self.assertEqual(thumbnail.path, path)
        self.assertLessEqual(thumbnail.width, 100)
        self.assertLessEqual(thumbnail.height, 50)
        self.assertEqual(thumbnail.format, 'JPEG')
        self.assertGreaterEqual(thumbnail.accessed_time, original_accessed_time)
        self.assertEqual(thumbnail.created_time, original_created_time)
        self.assertEqual(thumbnail.modified_time, original_modified_time)
        self.assertEqual(thumbnail.size, original_size)
        self.assertTrue(thumbnail.closed)

    def test_proxy_configuration(self):
        configuration = ConfigurationProxy(
            width=100,
            height=50,
        )
        self.assertEqual(configuration.key, 'w100_h50')
        key = '/'.join((configuration.key, 'wolf.jpg'))
        key = md5(force_bytes(key)).digest()
        key = b64encode(key, b'ab').decode('ascii')[:6]
        path = os.path.join(
            self.temp_dir,
            'thumbs',
            'wolf_{0}.jpg'.format(key),
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
        self.assertFalse(thumbnail.closed)

        thumbnail = self.source.get_existing_thumbnail(configuration)
        self.assertEqual(thumbnail.path, path)
        self.assertLessEqual(thumbnail.width, configuration.width)
        self.assertLessEqual(thumbnail.height, configuration.height)
        self.assertEqual(thumbnail.format, configuration.format)
        self.assertGreaterEqual(thumbnail.accessed_time, original_accessed_time)
        self.assertEqual(thumbnail.created_time, original_created_time)
        self.assertEqual(thumbnail.modified_time, original_modified_time)
        self.assertEqual(thumbnail.size, original_size)
        self.assertTrue(thumbnail.closed)

        thumbnail = self.source.get_thumbnail(configuration)
        self.assertEqual(thumbnail.path, path)
        self.assertLessEqual(thumbnail.width, configuration.width)
        self.assertLessEqual(thumbnail.height, configuration.height)
        self.assertEqual(thumbnail.format, configuration.format)
        self.assertGreaterEqual(thumbnail.accessed_time, original_accessed_time)
        self.assertEqual(thumbnail.created_time, original_created_time)
        self.assertEqual(thumbnail.modified_time, original_modified_time)
        self.assertEqual(thumbnail.size, original_size)
        self.assertTrue(thumbnail.closed)

