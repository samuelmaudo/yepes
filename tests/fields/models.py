# -*- coding:utf-8 -*-

from Crypto.Cipher import AES, ARC2, ARC4, Blowfish, CAST, DES, DES3, XOR

from django.db import models
from django.utils import six
from django.utils.six.moves import xrange

from yepes.fields import (
    BitField,
    CompressedTextField,
    EncryptedTextField,
    FormulaField,
    PickledObjectField,
    RelatedBitField,
    SlugField,
)


class BitModel(models.Model):

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

    def __str__(self):
        return six.text_type(self.flags)

    __unicode__ = __str__


class CompressedModel(models.Model):

    default = CompressedTextField()
    level_3 = CompressedTextField(
            compression_level=3)
    level_6 = CompressedTextField(
            compression_level=6)
    level_9 = CompressedTextField(
            compression_level=9)


class EncryptedModel(models.Model):

    default = EncryptedTextField()
    aes = EncryptedTextField(
            cipher=AES)
    arc2 = EncryptedTextField(
            cipher=ARC2)
    #arc4 = EncryptedTextField(
            #cipher=ARC4)
    blowfish = EncryptedTextField(
            cipher=Blowfish)
    cast = EncryptedTextField(
            cipher=CAST)
    des = EncryptedTextField(
            cipher=DES)
    des3 = EncryptedTextField(
            cipher=DES3)
    #xor = EncryptedTextField(
            #cipher=XOR)


class FlagModel(models.Model):

    name = models.CharField(
            max_length=31)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    __unicode__ = __str__


class FormulaModel(models.Model):

    permissive_formula = FormulaField(
            blank=True)
    restricted_formula = FormulaField(
            blank=True,
            variables=('x', 'y', 'z'))


class LongBitModel(models.Model):

    FLAG_CHOICES = [
        (i, bin(i)[2:])
        for i in xrange(128)
    ]
    flags = BitField(
            choices=FLAG_CHOICES)
    related_flags = RelatedBitField(
            'FlagModel',
            allowed_choices=128)

    class Meta:
        ordering = ['id']


class PickledModel(models.Model):

    default = PickledObjectField()
    protocol_0 = PickledObjectField(
            protocol=0)
    protocol_1 = PickledObjectField(
            protocol=1)
    protocol_2 = PickledObjectField(
            protocol=2)


class RelatedBitModel(models.Model):

    flags = RelatedBitField(
            'FlagModel')

    class Meta:
        ordering = ['id']

    def __str__(self):
        return six.text_type(self.flags)

    __unicode__ = __str__


class SlugModel(models.Model):

    title = models.CharField(
            max_length=63)
    slug = SlugField(
            max_length=63)
    unique_slug = SlugField(
            max_length=63,
            unique=True)

    filter_field = models.BooleanField(
            default=False)
    relatively_unique_slug = SlugField(
            max_length=63,
            unique_with_respect_to='filter_field')

    def __str__(self):
        return self.title

    __unicode__ = __str__

