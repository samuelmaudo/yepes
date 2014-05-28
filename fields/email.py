# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from django import forms
from django.core.validators import validate_email
from django.db import models
from django.utils.translation import ugettext_lazy as _

from yepes.utils.email import normalize_email


class EmailField(models.CharField):
    default_validators = [validate_email]
    description = _('Email address')

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('max_length', 63)
        super(EmailField, self).__init__(*args, **kwargs)

    def clean(self, value, model_instance):
        value = super(EmailField, self).clean(value, model_instance)
        if value is None:
            return value
        else:
            return normalize_email(value)

    def formfield(self, **kwargs):
        kwargs.setdefault('form_class', forms.EmailField)
        field = super(models.CharField, self).formfield(**kwargs)
        field.validators = self.validators
        return field

    def south_field_triple(self):
        """
        Returns a suitable description of this field for South.
        """
        from south.modelsinspector import introspector
        field_class = 'django.db.models.fields.CharField'
        args, kwargs = introspector(self)
        return (field_class, args, kwargs)

