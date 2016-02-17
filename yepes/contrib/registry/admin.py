# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from collections import OrderedDict

from django.contrib.admin.views.main import ChangeList as BaseChangeList
from django.contrib.admin.util import quote
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse
from django.forms.fields import CharField, IntegerField
from django.forms.forms import Form as BaseForm
from django.forms.widgets import HiddenInput

from yepes import admin
from yepes.contrib.registry.base import registry, REGISTRY_KEYS
from yepes.contrib.registry.forms import EntryFormSet
from yepes.contrib.registry.models import Entry, LongEntry


class ChangeList(BaseChangeList):

    def get_results(self, request):
        self.result_list = self.get_queryset(request)
        self.result_count = len(self.result_list)
        self.full_result_count = self.result_count
        self.show_all = True
        self.can_show_all = True
        self.multi_page = False
        self.paginator = None

    def get_queryset(self, request):
        return self.root_query_set

    def url_for_result(self, result):
        return reverse('admin:{0}_{1}_change'.format(self.opts.app_label,
                                                     self.opts.model_name),
                       args=(quote(result.key), ),
                       current_app=self.model_admin.admin_site.name)


class EntryAdmin(admin.ModelAdmin):

    fields = ['key', 'value']
    list_display = ['key', 'value']
    list_editable = ['value']
    readonly_fields = ['key']

    def _has_add_permission(self, request):
        return False

    #def _has_change_permission(self, request, obj):
        #return False

    def _has_delete_permission(self, request, obj):
        return False

    #def _has_view_permission(self, request, obj):
        #return False

    def delete_model(self, request, obj):
        pass

    def get_actions(self, request):
        return OrderedDict()

    def get_changelist(self, request, **kwargs):
        return ChangeList

    def get_changelist_formset(self, request):
        return EntryFormSet

    def get_form(self, request, obj=None, **kwargs):
        value_field = REGISTRY_KEYS[obj.key]
        value_field.initial = obj.value
        class EntryForm(BaseForm):
            id = IntegerField(required=False, widget=HiddenInput)
            key = CharField(required=False, widget=HiddenInput)
            value = value_field

        return EntryForm

    def get_object(self, request, key):
        for entry in self.get_queryset(request):
            if entry.key == key:
                return entry

    def get_queryset(self, request):
        current_site = Site.objects.get_current()
        registry_keys = list(registry.keys())
        registry_keys.sort()
        return [
            Entry(i+1, current_site, key, registry.get(key))
            for i, key
            in enumerate(registry_keys)
        ]

    def save_form(self, request, form, change):
        return Entry(key=form.initial['key'], value=form.cleaned_data['value'])

    def save_model(self, request, obj, form, change):
        registry[obj.key] = obj.value


admin.site.register(Entry, EntryAdmin)

