# -*- coding:utf-8 -*-

from __future__ import unicode_literals

import os

from django.core.files.storage import FileSystemStorage

from yepes.apps import apps
from yepes.contrib.thumbnails.files import ImageFile, SourceFile
from yepes.test_mixins import TempDirMixin


class ThumbnailsMixin(TempDirMixin):

    def setUp(self):
        super(ThumbnailsMixin, self).setUp()
        app_config = apps.get_app_config('thumbnails')
        app_static_dir = os.path.join(app_config.path, 'static')
        app_storage = FileSystemStorage(app_static_dir)
        temp_storage = FileSystemStorage(self.temp_dir)
        dirnames, filenames = app_storage.listdir('thumbnails')
        for name in filenames:
            file = app_storage.open('/'.join(('thumbnails', name)))
            temp_storage.save(name, file)
            file.close()

        self.source_image = ImageFile(temp_storage.open('wolf.jpg'))
        self.source = SourceFile(self.source_image, storage=temp_storage)
        self.temp_storage = temp_storage

    def tearDown(self):
        self.source.close()
        super(ThumbnailsMixin, self).tearDown()

