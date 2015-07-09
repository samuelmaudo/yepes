# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from django import forms


class TextField(forms.CharField):
    widget = forms.Textarea

