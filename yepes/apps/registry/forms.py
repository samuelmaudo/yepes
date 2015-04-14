# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from django.contrib.sites.models import Site
from django.forms.fields import CharField, IntegerField
from django.forms.forms import Form as BaseForm
from django.forms.models import BaseModelFormSet
from django.forms.widgets import HiddenInput

from yepes.apps.registry.base import registry, REGISTRY_KEYS
from yepes.apps.registry.models import Entry
from yepes.utils.properties import cached_property


class EntryFormSet(BaseModelFormSet):

    absolute_max = 1000
    can_delete = False
    can_order = False
    extra=0
    form = None
    max_num = None
    model = Entry
    validate_max = False

    def _construct_form(self, entry, **kwargs):
        value_field = REGISTRY_KEYS[entry.key]
        value_field.initial = entry.value
        class EntryForm(BaseForm):
            id = IntegerField(required=False, widget=HiddenInput)
            key = CharField(required=False, widget=HiddenInput)
            value = value_field
            def save_m2m(self):
                pass

        defaults = {
            'auto_id': self.auto_id,
            'initial': {'id': entry.id, 'key': entry.key, 'value': entry.value},
            'error_class': self.error_class,
            'prefix': self.add_prefix(entry.id),
        }
        defaults.update(**kwargs)
        if self.is_bound:
            defaults['data'] = self.data
            defaults['files'] = self.files

        form = EntryForm(**defaults)
        self.add_fields(form, entry.id)
        return form

    def add_fields(self, *args, **kwargs):
        super(BaseModelFormSet, self).add_fields(*args, **kwargs)

    def get_queryset(self):
        if self.queryset is None:
            current_site = Site.objects.get_current()
            registry_keys = list(registry.keys())
            registry_keys.sort()
            self.queryset = [
                self.model(i+1, current_site, key, registry.get(key))
                for i, key
                in enumerate(registry_keys)
            ]
        return self.queryset

    def initial_form_count(self):
        return len(self.get_queryset())

    def total_form_count(self):
        return len(self.get_queryset())

    def validate_unique(self):
        pass

    @cached_property
    def forms(self):
        forms = []
        for entry in self.get_queryset():
            forms.append(self._construct_form(entry))
        return forms

