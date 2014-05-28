# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from django import forms
from django.forms.models import ModelForm, ModelFormMetaclass
from django.utils import six


class PropertiesModelFormMetaclass(ModelFormMetaclass):

    def __new__(cls, name, bases, attrs):
        options = attrs.get('Meta')
        for base in reversed(bases):
            if options is None:
                options = getattr(base, 'Meta', None)

        if options is None or options.model is None:
            properties = []
        else:
            info = attrs.get('Properties')
            for base in reversed(bases):
                if info is None:
                    info = getattr(base, 'Properties', None)

            property_names = {
                attr_name
                for attr_name
                in dir(info)
                if not attr_name.startswith('_')
            }
            properties = [
                (property_name, getattr(info, property_name))
                for property_name
                in property_names
            ]
            if getattr(options, 'fields', None) is not None:
                properties = [
                    (property_name, verbose_name)
                    for property_name, verbose_name
                    in properties
                    if property_name in options.fields
                ]
                options.fields = [
                    field_name
                    for field_name
                    in options.fields
                    if field_name not in property_names
                ]
            if getattr(options, 'exclude', None) is not None:
                properties = [
                    (property_name, verbose_name)
                    for property_name, verbose_name
                    in properties
                    if property_name not in options.exclude
                ]
                options.exclude = [
                    field_name
                    for field_name
                    in options.exclude
                    if field_name not in property_names
                ]
        super_new = super(PropertiesModelFormMetaclass, cls).__new__
        new_cls = super_new(cls, name, bases, attrs)
        new_cls._meta.properties = properties
        for property_name, verbose_name in properties:
            field = forms.CharField(label=verbose_name, required=False)
            field.widget.attrs['readonly'] = True
            new_cls.base_fields[property_name] = field

        return new_cls


@six.add_metaclass(PropertiesModelFormMetaclass)
class PropertiesModelForm(ModelForm):

    def __init__(self, *args, **kwargs):
        super(PropertiesModelForm, self).__init__(*args, **kwargs)
        for property_name, verbose_name in self._meta.properties:
            value = getattr(self.instance, property_name)
            if callable(value):
                value = value()
            self.initial[property_name] = value

