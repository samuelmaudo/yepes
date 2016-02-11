# -*- coding:utf-8 -*-

from __future__ import unicode_literals


class AdminMixin(object):

    modeladmin = None

    def add_preserved_filters(self, url):
        filters = self.request.GET.get('_changelist_filters')
        if filters:
            url = ''.join((
                url,
                '&' if '?' in url else '?',
                filters,
            ))
        return url

    def get_modeladmin(self):
        return self.modeladmin

    def get_queryset(self):
        modeladmin = self.get_modeladmin()
        if modeladmin is None:
            return None

        # This ugly hack is required to use ChangeList to filter the queryset.
        request = self.request
        original_params = request.GET
        ids = original_params.get('_selected_ids')
        filters = original_params.get('_changelist_filters')

        if filters:
            lookups = [
                lookup.split('=', 1)
                for lookup
                in filters.split('&')
            ]
            request.GET = dict(lookups)
        else:
            request.GET = {}

        list_display = modeladmin.get_list_display(request)
        list_display_links = modeladmin.get_list_display_links(request, list_display)
        list_filter = modeladmin.get_list_filter(request)

        ChangeList = modeladmin.get_changelist(request)
        cl = ChangeList(
            request, modeladmin.model, list_display, list_display_links,
            list_filter, modeladmin.date_hierarchy, modeladmin.search_fields,
            modeladmin.list_select_related, modeladmin.list_per_page,
            modeladmin.list_max_show_all, modeladmin.list_editable,
            modeladmin,
        )
        qs = cl.get_queryset(request)
        if ids:
            qs = qs.filter(pk__in=ids.split(','))

        # Do not forget to restore the original parameters.
        request.GET = original_params

        return qs

