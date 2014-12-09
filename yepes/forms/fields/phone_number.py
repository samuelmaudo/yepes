# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from django import forms

from yepes.validators import PhoneNumberValidator


class PhoneNumberField(forms.CharField):

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('max_length', 31)
        kwargs.setdefault('validators', [PhoneNumberValidator()])
        super(PhoneNumberField, self).__init__(*args, **kwargs)

