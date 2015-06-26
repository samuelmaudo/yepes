# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from Crypto.Cipher import AES, ARC2, ARC4, Blowfish, CAST, DES, DES3, XOR

from django.db import models
from django.utils import six
from django.utils.six.moves import range

from yepes.cache import LookupTable

from yepes.fields import (
    BitField,
    CachedForeignKey,
    CharField,
    ColorField,
    CommaSeparatedField,
    CompressedTextField,
    EmailField,
    EncryptedCharField,
    EncryptedTextField,
    FormulaField,
    GuidField,
    IdentifierField,
    PhoneNumberField,
    PickledObjectField,
    PostalCodeField,
    RelatedBitField,
    RichTextField,
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


class CachedForeignKeyModel(models.Model):

    mandatory_key = CachedForeignKey(
            'CachedModel',
            blank=False,
            null=False,
            related_name='+')
    optional_key = CachedForeignKey(
            'CachedModel',
            blank=True,
            null=True,
            related_name='+')

    mandatory_key_with_default_value = CachedForeignKey(
            'CachedModelWithDefaultValue',
            blank=False,
            null=False,
            related_name='+')
    optional_key_with_default_value = CachedForeignKey(
            'CachedModelWithDefaultValue',
            blank=True,
            null=True,
            related_name='+')


class CachedModel(models.Model):

    cache = LookupTable()


class CachedModelWithDefaultValue(models.Model):

    cache = LookupTable(
            default_from_registry='tests:DEFAULT_CACHED_MODEL')


class ColoredModel(models.Model):

    color = ColorField()


class CommaSeparatedModel(models.Model):

    default_separator = CommaSeparatedField()
    custom_separator = CommaSeparatedField(separator='|')


class CompressedModel(models.Model):

    default = CompressedTextField()
    level_3 = CompressedTextField(
            compression_level=3)
    level_6 = CompressedTextField(
            compression_level=6)
    level_9 = CompressedTextField(
            compression_level=9)


class EmailModel(models.Model):

    email = EmailField()


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

    name = CharField(
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


class GuidModel(models.Model):

    default_charset = GuidField(unique=True)
    custom_charset = GuidField(charset='z%,#8+ç@', unique=True)


class IdentifierModel(models.Model):

    key = IdentifierField()


class LongBitModel(models.Model):

    FLAG_CHOICES = [
        (i, bin(i)[2:])
        for i in range(128)
    ]
    flags = BitField(
            choices=FLAG_CHOICES)
    related_flags = RelatedBitField(
            'FlagModel',
            allowed_choices=128)

    class Meta:
        ordering = ['id']


class PhoneNumberModel(models.Model):

    phone = PhoneNumberField()


class PickledModel(models.Model):

    default = PickledObjectField()
    protocol_0 = PickledObjectField(
            protocol=0)
    protocol_1 = PickledObjectField(
            protocol=1)
    protocol_2 = PickledObjectField(
            protocol=2)


class PostalCodeModel(models.Model):

    code = PostalCodeField()


class RelatedBitModel(models.Model):

    flags = RelatedBitField(
            'FlagModel')

    class Meta:
        ordering = ['id']

    def __str__(self):
        return six.text_type(self.flags)

    __unicode__ = __str__


class RichTextModel(models.Model):

    text = RichTextField()
    upper_text = RichTextField(
            processors=[lambda x: x.upper()],
            store_html=False)


class SlugModel(models.Model):

    title = CharField(
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

