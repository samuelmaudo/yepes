# -*- coding:utf-8 -*-

from __future__ import unicode_literals

import shutil
import tempfile
import warnings

from django.utils import six


class TempDirMixin(object):

    tempDirPrefix = None

    def setUp(self):
        """
        Creates a pristine temp directory.
        """
        super(TempDirMixin, self).setUp()
        if self.tempDirPrefix is not None:
            prefix = self.tempDirPrefix
        else:
            prefix = 'test_'
        self.temp_dir = tempfile.mkdtemp(prefix=prefix)

    def tearDown(self):
        """
        Removes temp directory and all its contents.
        """
        super(TempDirMixin, self).tearDown()
        try:
            shutil.rmtree(six.text_type(self.temp_dir))
        except OSError:
            msg = 'Failed to remove temp directory: {0}'
            warnings.warn(msg.format(self.temp_dir), RuntimeWarning)

