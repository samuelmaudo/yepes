# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from django import forms

from .models import (
    BitModel,
    CachedForeignKeyModel,
    ColoredModel,
    CommaSeparatedModel,
    CompressedModel,
    EmailModel,
    EncryptedModel,
    FlagModel,
    FormulaModel,
    GuidModel,
    IdentifierModel,
    LongBitModel,
    PhoneNumberModel,
    PickledModel,
    PostalCodeModel,
    RelatedBitModel,
    RichTextModel,
    SlugModel,
)


class BitForm(forms.ModelForm):
    class Meta:
        model = BitModel


class CachedForeignKeyForm(forms.ModelForm):
    class Meta:
        model = CachedForeignKeyModel


class ColoredForm(forms.ModelForm):
    class Meta:
        model = ColoredModel


class CommaSeparatedForm(forms.ModelForm):
    class Meta:
        model = CommaSeparatedModel


class CompressedForm(forms.ModelForm):
    class Meta:
        model = CompressedModel


class EmailForm(forms.ModelForm):
    class Meta:
        model = EmailModel


class EncryptedForm(forms.ModelForm):
    class Meta:
        model = EncryptedModel


class FlagForm(forms.ModelForm):
    class Meta:
        model = FlagModel


class FormulaForm(forms.ModelForm):
    class Meta:
        model = FormulaModel


class GuidForm(forms.ModelForm):
    class Meta:
        model = GuidModel


class IdentifierForm(forms.ModelForm):
    class Meta:
        model = IdentifierModel


class LongBitForm(forms.ModelForm):
    class Meta:
        model = LongBitModel


class PhoneNumberForm(forms.ModelForm):
    class Meta:
        model = PhoneNumberModel


class PickledForm(forms.ModelForm):
    class Meta:
        model = PickledModel


class PostalCodeForm(forms.ModelForm):
    class Meta:
        model = PostalCodeModel


class RelatedBitForm(forms.ModelForm):
    class Meta:
        model = RelatedBitModel


class RichTextForm(forms.ModelForm):
    class Meta:
        model = RichTextModel


class SlugForm(forms.ModelForm):
    class Meta:
        model = SlugModel

