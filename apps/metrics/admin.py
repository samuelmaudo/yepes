# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _

from yepes import admin
from yepes.loading import get_model

Browser = get_model('metrics', 'Browser')
Engine = get_model('metrics', 'Engine')
Platform = get_model('metrics', 'Platform')
Page = get_model('metrics', 'Page')
PageView = get_model('metrics', 'PageView')
Referrer = get_model('metrics', 'Referrer')
ReferrerPage = get_model('metrics', 'ReferrerPage')
Visit = get_model('metrics', 'Visit')
Visitor = get_model('metrics', 'Visitor')


class PageAdmin(admin.ReadOnlyMixin, admin.ModelAdmin):
    pass


class PageViewAdmin(admin.ReadOnlyMixin, admin.ModelAdmin):

    date_hierarchy = 'date'
    fieldsets = [
        (None, {
            'fields': [
                'date',
                'visit',
                'page',
                'status_code',
                'load_time',
                'previous_page',
                'next_page',
            ],
        }),
    ]
    list_display = ['date', 'page', 'status_code', 'load_time']
    readonly_fields = ['previous_page', 'next_page']


class PageViewInline(admin.ReadOnlyMixin, admin.TabularInline):
    extra = 0
    fields = ['date', 'page', 'status_code', 'load_time']
    model = PageView
    verbose_name = _('View')
    verbose_name_plural = _('Views')


class ParameterAdmin(admin.ModelAdmin):

    change_list_template = 'admin/change_list_filter_sidebar.html'
    change_list_filter_template = 'admin/filter_listing.html'
    fieldsets = [
        (None, {
            'fields': [
                'name',
                ('token', 'regex'),
                'parent',
            ],
        }),
    ]
    list_display = ['name', 'token', 'index']
    list_editable = ['index']
    list_filter = ['parent']
    search_fields = ['name']
    ordering = ['tree_id', 'lft']


class ReferrerPageInline(admin.ReadOnlyMixin, admin.TabularInline):
    extra = 0
    fields = ['full_path']
    model = ReferrerPage
    verbose_name = _('Page')
    verbose_name_plural = _('Pages')


class ReferrerAdmin(admin.ReadOnlyMixin, admin.ModelAdmin):
    fields = ['domain']
    inlines = [ReferrerPageInline]
    list_display = ['domain']
    search_fields = ['domain']


class VisitAdmin(admin.ReadOnlyMixin, admin.ModelAdmin):

    change_list_template = 'admin/change_list_filter_sidebar.html'
    date_hierarchy = 'end_date'
    fieldsets = [
        (None, {
            'fields': [
                'start_date',
                'end_date',
                'visitor',
                'language',
                'country',
                'region',
                'browser',
                'engine',
                'platform',
                'referrer',
                'referrer_page',
                'user_agent',
            ],
        }),
    ]
    inlines = [PageViewInline]
    list_display = [
        'start_date',
        'page_count',
        'language',
        'country',
        'browser',
        'engine',
        'platform',
    ]
    list_filter = [
        'visitor__is_authenticated',
        'language',
        'country',
        'region',
        'browser',
        'engine',
        'platform',
    ]
    search_fields = [
        'user_agent',
    ]


class VisitorAdmin(admin.ReadOnlyMixin, admin.ModelAdmin):

    change_list_template = 'admin/change_list_filter_sidebar.html'
    fieldsets = [
        (None, {
            'fields': [
                'key',
                'is_authenticated',
            ],
        }),
    ]
    list_display = [
        'key',
        'is_authenticated',
    ]
    list_filter = [
        'is_authenticated',
    ]
    search_fields = [
        'key',
    ]


admin.site.register(Browser, ParameterAdmin)
admin.site.register(Engine, ParameterAdmin)
admin.site.register(Platform, ParameterAdmin)
admin.site.register(Page, PageAdmin)
admin.site.register(PageView, PageViewAdmin)
admin.site.register(Referrer, ReferrerAdmin)
admin.site.register(Visit, VisitAdmin)
admin.site.register(Visitor, VisitorAdmin)

