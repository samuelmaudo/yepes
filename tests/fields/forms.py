# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from django import forms

from .models import (
    BitModel,
    BooleanModel,
    CachedForeignKeyModel,
    ColoredModel,
    CommaSeparatedModel,
    CompressedModel,
    DecimalModel,
    EmailModel,
    EncryptedModel,
    FlagModel,
    FloatModel,
    FormulaModel,
    GuidModel,
    IdentifierModel,
    IntegerModel,
    LongBitModel,
    PhoneNumberModel,
    PickledModel,
    PostalCodeModel,
    RelatedBitModel,
    RichTextModel,
    SlugModel,
    TextModel,
)


class BitForm(forms.ModelForm):
    class Meta:
        fields = '__all__'
        model = BitModel


class BooleanForm(forms.ModelForm):
    class Meta:
        fields = '__all__'
        model = BooleanModel


class CachedForeignKeyForm(forms.ModelForm):
    class Meta:
        fields = '__all__'
        model = CachedForeignKeyModel


class ColoredForm(forms.ModelForm):
    class Meta:
        fields = '__all__'
        model = ColoredModel


class CommaSeparatedForm(forms.ModelForm):
    class Meta:
        fields = '__all__'
        model = CommaSeparatedModel


class CompressedForm(forms.ModelForm):
    class Meta:
        fields = '__all__'
        model = CompressedModel


class DecimalForm(forms.ModelForm):
    class Meta:
        fields = '__all__'
        model = DecimalModel


class EmailForm(forms.ModelForm):
    class Meta:
        fields = '__all__'
        model = EmailModel


class EncryptedForm(forms.ModelForm):
    class Meta:
        fields = '__all__'
        model = EncryptedModel


class FlagForm(forms.ModelForm):
    class Meta:
        fields = '__all__'
        model = FlagModel


class FloatForm(forms.ModelForm):
    class Meta:
        fields = '__all__'
        model = FloatModel


class FormulaForm(forms.ModelForm):
    class Meta:
        fields = '__all__'
        model = FormulaModel


class GuidForm(forms.ModelForm):
    class Meta:
        fields = '__all__'
        model = GuidModel


class IdentifierForm(forms.ModelForm):
    class Meta:
        fields = '__all__'
        model = IdentifierModel


class IntegerForm(forms.ModelForm):
    class Meta:
        fields = '__all__'
        model = IntegerModel


class LongBitForm(forms.ModelForm):
    class Meta:
        fields = '__all__'
        model = LongBitModel


class PhoneNumberForm(forms.ModelForm):
    class Meta:
        fields = '__all__'
        model = PhoneNumberModel


class PickledForm(forms.ModelForm):
    class Meta:
        fields = '__all__'
        model = PickledModel


class PostalCodeForm(forms.ModelForm):
    class Meta:
        fields = '__all__'
        model = PostalCodeModel


class RelatedBitForm(forms.ModelForm):
    class Meta:
        fields = '__all__'
        model = RelatedBitModel


class RichTextForm(forms.ModelForm):
    class Meta:
        fields = '__all__'
        model = RichTextModel


class SlugForm(forms.ModelForm):
    class Meta:
        fields = '__all__'
        model = SlugModel


class TextForm(forms.ModelForm):
    class Meta:
        fields = '__all__'
        model = TextModel

