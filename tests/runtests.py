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
        'yepes.apps.registry',
    ],
)


if __name__ == '__main__':
    failures = program.run()
    if failures > 0:
        sys.exit(True)

