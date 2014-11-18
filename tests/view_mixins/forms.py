# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from django import forms


class JsonMixinForm(forms.Form):

    boolean = forms.BooleanField()
    char = forms.CharField(
            min_length=3,
            max_length=6)
    integer = forms.IntegerField(
            min_value=3,
            max_value=6)

