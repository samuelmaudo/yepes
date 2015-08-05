# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from datetime import date, datetime, time
from decimal import Decimal

from django.db import models
from django.utils.timezone import utc as UTC


class MassUpdateModel(models.Model):

    binary = models.BinaryField(
            default=b'abc')
    boolean = models.BooleanField(
            default=False)
    char = models.CharField(
            max_length=255,
            default='abc def')
    date = models.DateField(
            default=date(1986, 9, 25))
    date_time = models.DateTimeField(
            default=datetime(1986, 9, 25, 12, 0, 0, tzinfo=UTC))
    decimal = models.DecimalField(
            max_digits=8,
            decimal_places=2,
            default=Decimal('10.0'))
    float = models.FloatField(
            default=10.0)
    integer = models.IntegerField(
            default=10)
    null_boolean = models.NullBooleanField(
            default=False)
    text = models.TextField(
            default='abc def ghi')
    time = models.TimeField(
            default=time(12, 0, 0))

