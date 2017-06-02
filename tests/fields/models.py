# -*- coding:utf-8 -*-

from __future__ import division, unicode_literals

from collections import defaultdict
from decimal import Decimal as dec

from Crypto.Cipher import AES, ARC2, ARC4, Blowfish, CAST, DES, DES3, XOR

from django.db import models
from django.utils import six
from django.utils.six.moves import range

from yepes.cache import LookupTable

from yepes.fields import (
    BigIntegerField,
    BitField,
    BooleanField,
    CachedForeignKey,
    CharField,
    ColorField,
    CommaSeparatedField,
    CompressedTextField,
    DecimalField,
    EmailField,
    EncryptedCharField,
    EncryptedTextField,
    FloatField,
    FormulaField,
    GuidField,
    IdentifierField,
    IntegerField,
    NullBooleanField,
    PhoneNumberField,
    PickledObjectField,
    PostalCodeField,
    RelatedBitField,
    RichTextField,
    SlugField,
    SmallIntegerField,
    TextField,
)
from yepes.model_mixins import Calculated


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


class BooleanModel(models.Model):

    boolean = BooleanField()
    null_boolean = NullBooleanField()


class CachedForeignKeyModel(models.Model):

    mandatory_key = CachedForeignKey(
            'CachedModel',
            blank=False,
            null=False,
            on_delete=models.CASCADE,
            related_name='+')
    optional_key = CachedForeignKey(
            'CachedModel',
            blank=True,
            null=True,
            on_delete=models.CASCADE,
            related_name='+')

    mandatory_key_with_default_value = CachedForeignKey(
            'CachedModelWithDefaultValue',
            blank=False,
            null=False,
            on_delete=models.CASCADE,
            related_name='+')
    optional_key_with_default_value = CachedForeignKey(
            'CachedModelWithDefaultValue',
            blank=True,
            null=True,
            on_delete=models.CASCADE,
            related_name='+')


class CachedModel(models.Model):

    objects = models.Manager()
    cache = LookupTable()


class CachedModelWithDefaultValue(models.Model):

    objects = models.Manager()
    cache = LookupTable(
            default_registry_key='tests:DEFAULT_CACHED_MODEL')


CALCULATOR_CALLS = defaultdict(int)

class CalculatedModel(Calculated):

    boolean = BooleanField(calculated=True)
    char = CharField(calculated=True, max_length=10)
    decimal = DecimalField(calculated=True, max_digits=10, decimal_places=4)
    float = FloatField(calculated=True)
    integer = IntegerField(calculated=True)
    null_boolean = NullBooleanField(calculated=True)
    pickled_object = PickledObjectField(calculated=True)

    def calculate_boolean(self):
        CALCULATOR_CALLS['boolean'] += 1
        return bool(self.pk % 2 == 0)

    def calculate_char(self):
        CALCULATOR_CALLS['char'] += 1
        return 'even' if self.pk % 2 == 0 else 'odd'

    def calculate_decimal(self):
        CALCULATOR_CALLS['decimal'] += 1
        return dec('{0:.4}'.format(self.pk / 7))

    def calculate_float(self):
        CALCULATOR_CALLS['float'] += 1
        return float(self.pk / 7)

    def calculate_integer(self):
        CALCULATOR_CALLS['integer'] += 1
        return int(self.pk // 7)

    def calculate_null_boolean(self):
        CALCULATOR_CALLS['null_boolean'] += 1
        return bool(self.pk % 2 == 0)

    def calculate_pickled_object(self):
        CALCULATOR_CALLS['pickled_object'] += 1
        return dec('{0:.4}'.format(self.pk / 7)).as_tuple()


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


class DecimalModel(models.Model):

    decimal = DecimalField(
        max_digits=6,
        decimal_places=2)
    null_decimal = DecimalField(
        max_digits=6,
        decimal_places=2,
        blank=True,
        null=True)
    positive_decimal = DecimalField(
        max_digits=6,
        decimal_places=2,
        min_value=dec('0'),
        max_value=dec('100'))


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


class FloatModel(models.Model):

    float = FloatField()
    null_float = FloatField(blank=True, null=True)
    positive_float = FloatField(min_value=0.0, max_value=100.0)


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


class IntegerModel(models.Model):

    integer = IntegerField()
    null_integer = IntegerField(blank=True, null=True)
    positive_integer = IntegerField(min_value=0, max_value=100)

    big_integer = BigIntegerField()
    null_big_integer = BigIntegerField(blank=True, null=True)
    positive_big_integer = BigIntegerField(min_value=0, max_value=100)

    small_integer = SmallIntegerField()
    null_small_integer = SmallIntegerField(blank=True, null=True)
    positive_small_integer = SmallIntegerField(min_value=0, max_value=100)


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


class TextModel(models.Model):

    text = TextField(blank=True)
    limited_text = TextField(min_length=10, max_length=50)

