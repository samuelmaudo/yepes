#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os
import sys
import tempfile

from django.utils._os import upath

from yepes.test.program import TestProgram


program = TestProgram(
    workingDir=os.path.abspath(os.path.dirname(upath(__file__))),
    tempDir=tempfile.mkdtemp(prefix='yepes_'),
    templatesDir='templates',
    subdirsToSkip=[
        'requirements',
        'templates',
    ],
    alwaysInstalledApps=[
        'django.contrib.admin',
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sites',
        'mptt',
        'yepes',
        'yepes.contrib.datamigrations',
        'yepes.contrib.emails',
        'yepes.contrib.metrics',
        'yepes.contrib.newsletters',
        'yepes.contrib.registry',
        'yepes.contrib.sitemaps',
        'yepes.contrib.slugs',
        'yepes.contrib.standards',
        'yepes.contrib.thumbnails',
    ],
)


if __name__ == '__main__':
    failures = program.run()
    if failures > 0:
        sys.exit(True)

