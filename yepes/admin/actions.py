# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from django.contrib.admin import ACTION_CHECKBOX_NAME
from django.contrib.admin.actions import delete_selected
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext_lazy as _


delete_selected.short_description = _('Delete selected {verbose_name_plural}')


def export_csv(modeladmin, request, queryset):
    url_name = 'admin:{app_label}_{model_name}_exportcsv'
    return _redirect_to(url_name, modeladmin, request, queryset)
export_csv.short_description = _('Export selected {verbose_name_plural} as CSV')


def export_json(modeladmin, request, queryset):
    url_name = 'admin:{app_label}_{model_name}_exportjson'
    return _redirect_to(url_name, modeladmin, request, queryset)
export_json.short_description = _('Export selected {verbose_name_plural} as JSON')


def export_tsv(modeladmin, request, queryset):
    url_name = 'admin:{app_label}_{model_name}_exporttsv'
    return _redirect_to(url_name, modeladmin, request, queryset)
export_tsv.short_description = _('Export selected {verbose_name_plural} as TSV')


def export_yaml(modeladmin, request, queryset):
    url_name = 'admin:{app_label}_{model_name}_exportyaml'
    return _redirect_to(url_name, modeladmin, request, queryset)
export_yaml.short_description = _('Export selected {verbose_name_plural} as YAML')


def mass_update(modeladmin, request, queryset):
    url_name = 'admin:{app_label}_{model_name}_massupdate'
    return _redirect_to(url_name, modeladmin, request, queryset)
mass_update.short_description = _('Update selected {verbose_name_plural}')


def _redirect_to(url_name, modeladmin, request, queryset):
    opts = modeladmin.model._meta
    url = reverse(url_name.format(
            app_label=opts.app_label,
            model_name=opts.model_name))

    filters = modeladmin.get_preserved_filters(request)
    if filters:
        url = ''.join((
            url,
            '&' if '?' in url else '?',
            filters,
        ))

    if request.POST.get('select_across') not in ('true', '1'):
        ids = request.POST.getlist(ACTION_CHECKBOX_NAME)
        url = ''.join((
            url,
            '&' if '?' in url else '?',
            '_selected_ids=',
            ','.join(ids),
        ))

    return HttpResponseRedirect(url)

