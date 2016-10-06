# -*- coding:utf-8 -*-

from __future__ import absolute_import

import collections
import types

from django import VERSION as DJANGO_VERSION
from django.db import connections, router
from django.db.models import (
    Field,
    ForeignKey,
    Manager,
    QuerySet,
)
from django.db.models.fields.related import ForeignObjectRel
from django.utils import six


if DJANGO_VERSION < (1, 9):
    Field.remote_field = property(lambda self: self.rel)
    ForeignKey.target_field = ForeignKey.related_field
    ForeignObjectRel.model = property(lambda self: self.to)


def in_batches(self, batch_size):
    """
    Makes an iterator that returns batches of the indicated size with the
    results from applying this QuerySet to the database.

    WARNING: Each batch is an evaluated QuerySet, so its results are already
    cached.

    """
    start = 0
    stop = batch_size
    batch = self[start:stop]
    while batch:
        yield batch
        start += batch_size
        stop += batch_size
        batch = self[start:stop]

if six.PY2:
    in_batches = types.MethodType(in_batches, None, QuerySet)

setattr(QuerySet, 'in_batches', in_batches)


def in_batches(self, *args, **kwargs):
    return self.get_queryset().in_batches(*args, **kwargs)

def truncate(self):
    """
    Quickly removes all records of the Manager's model and tries to restart
    sequences owned by fields of the truncated model.

    NOTE: Sequence restarting currently is only supported by postgresql backend.

    """
    opts = self.model._meta
    conn = connections[self.write_db]
    sql = statements.get_sql('truncate', conn.vendor)
    with conn.cursor() as cursor:
        cursor.execute(sql.format(table=opts.db_table))

def write_db(self):
    return self._db or router.db_for_write(self.model, **self._hints)

if six.PY2:
    in_batches = types.MethodType(in_batches, None, Manager)
    truncate = types.MethodType(truncate, None, Manager)

setattr(Manager, 'in_batches', in_batches)
setattr(Manager, 'read_db', Manager.db)
setattr(Manager, 'truncate', truncate)
setattr(Manager, 'write_db', property(write_db))


class Statements(object):

    def __init__(self):
        self.sql_statements = collections.defaultdict(dict)

    def get_sql(self, name, vendor=None):
        sql = self.sql_statements[vendor].get(name)
        if vendor is not None and not sql:
            sql = self.sql_statements[None].get(name)
        return sql

    def register(self, name, sql, vendor=None):
        self.sql_statements[vendor][name] = sql

statements = Statements()
statements.register('truncate', 'TRUNCATE "{table}" RESTART IDENTITY;', 'postgresql')
statements.register('truncate', 'TRUNCATE `{table}`;', 'mysql')
statements.register('truncate', 'DELETE FROM "{table}";')

