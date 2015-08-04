# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from django.contrib.staticfiles.storage import AppStaticStorage
from django.core.files.storage import FileSystemStorage

from yepes.apps.thumbnails.files import ImageFile, SourceFile
from yepes.test_mixins import TempDirMixin


class ThumbnailsMixin(TempDirMixin):

    def setUp(self):
        super(ThumbnailsMixin, self).setUp()
        app = AppStaticStorage('yepes.apps.thumbnails')
        temp = FileSystemStorage(self.temp_dir)
        dirnames, filenames = app.listdir('thumbnails')
        for name in filenames:
            file = app.open('/'.join(('thumbnails', name)))
            temp.save(name, file)
            file.close()

        self.source_image = ImageFile(temp.open('wolf.jpg'))
        self.source = SourceFile(self.source_image, storage=temp)
        self.temp_storage = temp

    def tearDown(self):
        self.source.close()
        super(ThumbnailsMixin, self).tearDown()

