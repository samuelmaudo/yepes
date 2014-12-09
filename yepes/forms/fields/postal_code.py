# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from django import forms

from yepes.validators import PostalCodeValidator


class PostalCodeField(forms.CharField):

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('max_length', 15)
        kwargs.setdefault('validators', [PostalCodeValidator()])
        super(PostalCodeField, self).__init__(*args, **kwargs)

