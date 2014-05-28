# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from django.db import models
from django.utils.six.moves import xrange

from yepes.fields import BitField, RelatedBitField


class BitTestModel(models.Model):

    FLAG_CHOICES = (
        ('bin', 'Binario'),
        ('dec', 'Decimal'),
        ('hex', 'Hexadecimal'),
        ('oct', 'Octal'),
    )
    flags = BitField(
            choices=FLAG_CHOICES,
            default=['bin', 'dec'])

    class Meta:
        ordering = ['id']

    def __unicode__(self):
        return unicode(self.flags)


class FlagTestModel(models.Model):

    name = models.CharField(
            max_length=31)

    class Meta:
        ordering = ['name']

    def __unicode__(self):
        return self.name


class RelatedBitTestModel(models.Model):

    flags = RelatedBitField(
            'FlagTestModel')

    class Meta:
        ordering = ['id']

    def __unicode__(self):
        return unicode(self.flags)


class LongBitTestModel(models.Model):

    FLAG_CHOICES = [
        (i, bin(i)[2:])
        for i in xrange(128)
    ]
    flags = BitField(
            choices=FLAG_CHOICES)
    related_flags = RelatedBitField(
            'FlagTestModel',
            allowed_choices=128)

    class Meta:
        ordering = ['id']

