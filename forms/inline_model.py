# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from django.forms.models import (
    inlineformset_factory,
    ModelForm, ModelFormMetaclass,
)
from django.utils import six


class InlineModelFormMetaclass(ModelFormMetaclass):

    def __new__(cls, name, bases, attrs):
        options = attrs.get('Meta')
        for base in reversed(bases):
            if options is None:
                options = getattr(base, 'Meta', None)

        inlines = getattr(options, 'inlines', ())
        super_new = super(InlineModelFormMetaclass, cls).__new__
        new_cls = super_new(cls, name, bases, attrs)
        new_cls._meta.inlines = inlines
        return new_cls


@six.add_metaclass(InlineModelFormMetaclass)
class InlineModelForm(ModelForm):

    def __init__(self, data=None, files=None, inlines=(), *args, **kwargs):
        super(InlineModelForm, self).__init__(data, files, *args, **kwargs)
        opts = self._meta
        model = self.instance.__class__
        self._inline_form_sets = []
        for field_name in (inlines or opts.inlines):
            kwargs = {'extra': 0}
            if not isinstance(field_name, six.string_types):
                kwargs.update(field_name[1])
                field_name = field_name[0]

            field = getattr(model, field_name).related
            FormSet = inlineformset_factory(model, field.model, **kwargs)
            form_set = FormSet(data=data, files=files, instance=self.instance)
            self._inline_form_sets.append(form_set)
            setattr(self, field_name, form_set)

    def is_valid(self):
        valid = super(InlineModelForm, self).is_valid()
        for form_set in self._inline_form_sets:
            if not form_set.is_valid():
                valid = False

        return valid

    def save(self, commit=True):
        instances = [super(InlineModelForm, self).save(commit=commit)]
        for form_set in self._inline_form_sets:
            instances.extend(form_set.save(commit=commit))

        return instances

