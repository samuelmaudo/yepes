# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from django.db.models import F, Q
from django.db.models import Case, Count, Sum, When
from django.db.models import Field, IntegerField


def CountIf(field, expression, **extra):
    return Count(Case(
        When(expression, then=F(field), **extra),
        default=None,
        output_field=Field(),
    ))


def SumIf(value, expression, **extra):
    output_field = extra.pop('output_field', None)
    if output_field is None:
        output_field = IntegerField()

    return Sum(Case(
        When(expression, then=value, **extra),
        default=output_field.to_python(0),
        output_field=output_field,
    ))

