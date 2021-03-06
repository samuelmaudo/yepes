# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from yepes import admin
from yepes.apps import apps

Configuration = apps.get_model('thumbnails', 'Configuration')
Source = apps.get_model('thumbnails', 'Source')
Thumbnail = apps.get_model('thumbnails', 'Thumbnail')


class ConfigurationAdmin(admin.ModelAdmin):

    fieldsets = [
        (None, {
            'fields': [
                'key',
            ],
        }),
        (None, {
            'fields': [
                'width',
                'height',
                'background',
            ],
        }),
        (None, {
            'fields': [
                'mode',
                'algorithm',
                'gravity',
            ],
        }),
        (None, {
            'fields': [
                'format',
                'quality',
            ],
        }),
    ]
    list_display = [
        'key',
        'width',
        'height',
        'background',
        'mode',
        'algorithm',
        'gravity',
        'format',
        'quality',
    ]
    search_fields = ['key']


class SourceAdmin(admin.ModelAdmin):

    date_hierarchy = 'last_modified'
    fieldsets = [
        (None, {
            'fields': [
                'name',
                'last_modified',
            ],
        }),
    ]
    list_display = [
        'name',
        'last_modified',
    ]
    search_fields = ['name']


class ThumbnailAdmin(admin.ModelAdmin):

    date_hierarchy = 'last_modified'
    fieldsets = [
        (None, {
            'fields': [
                'source',
                'name',
                'last_modified',
            ],
        }),
    ]
    list_display = [
        'source',
        'name',
        'last_modified',
    ]
    search_fields = ['name']


admin.site.register(Configuration, ConfigurationAdmin)
admin.site.register(Source, SourceAdmin)
admin.site.register(Thumbnail, ThumbnailAdmin)
