# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from django.contrib import admin
from django.contrib.admin.actions import delete_selected
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext_lazy as _


delete_selected.short_description = _('Delete selected {verbose_name_plural}')


def export(modeladmin, request, queryset):
    opts = modeladmin.model._meta
    url_name = 'admin:{0}_{1}_export'.format(
        opts.app_label,
        opts.model_name,
    )
    url = reverse(url_name)

    if request.POST.get('select_across') not in ('true', '1'):
        selected = request.POST.getlist(admin.ACTION_CHECKBOX_NAME)
        url += '?ids={0}'.format(','.join(selected))

    return HttpResponseRedirect(url)
export.short_description = _('Export selected {verbose_name_plural}')


def mass_update(modeladmin, request, queryset):
    opts = modeladmin.model._meta
    url_name = 'admin:{0}_{1}_massupdate'.format(
        opts.app_label,
        opts.model_name,
    )
    url = reverse(url_name)

    if request.POST.get('select_across') not in ('true', '1'):
        selected = request.POST.getlist(admin.ACTION_CHECKBOX_NAME)
        url += '?ids={0}'.format(','.join(selected))

    return HttpResponseRedirect(url)
mass_update.short_description = _('Update selected {verbose_name_plural}')

