# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from yepes.contrib.datamigrations.fields import *
from yepes.contrib.datamigrations.migrations import (
    CustomDataMigration,
    DataMigration,
    QuerySetExportation,
)

VERSION = (1, 0, 0, 'alpha', 0)

def get_version():
    from django.utils.version import get_version
    return get_version(VERSION)

default_app_config = 'yepes.contrib.datamigrations.apps.DataMigrationsConfig'
