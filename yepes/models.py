# -*- coding:utf-8 -*-

from __future__ import absolute_import

import types

from django import VERSION as DJANGO_VERSION
from django.db import connections
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
    qs = self.get_queryset()
    qs._for_write = True

    conn = connections[qs.db]
    statements = self.statements.get(conn.vendor)
    if statements is None:
        statements = self.statements['default']

    opts = self.model._meta
    cursor = conn.cursor()
    cursor.execute(statements['truncate'].format(table=opts.db_table))

if six.PY2:
    in_batches = types.MethodType(in_batches, None, Manager)
    truncate = types.MethodType(truncate, None, Manager)

setattr(Manager, 'in_batches', in_batches)
setattr(Manager, 'statements', {
    'postgresql': {
        'truncate': 'TRUNCATE "{table}" RESTART IDENTITY;',
    },
    'mysql': {
        'truncate': 'TRUNCATE `{table}`;',
    },
    'default': {
        'truncate': 'DELETE FROM "{table}";',
    },
})
setattr(Manager, 'truncate', truncate)

