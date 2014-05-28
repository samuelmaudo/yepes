# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _

from yepes import admin
from yepes.loading import get_model

Country = get_model('standards', 'Country')
CountrySubdivision = get_model('standards', 'CountrySubdivision')
Currency = get_model('standards', 'Currency')
Language = get_model('standards', 'Language')
Region = get_model('standards', 'Region')


class CountrySubdivisionInline(admin.StackedInline):

    fieldsets = [
        (None, {
            'fields': [
                'is_enabled',
                'name',
                'code',
                'name_en',
                'name_fr',
                'name_es',
                'name_zh',
                'name_ru',
                'name_de',
                'name_pt',
            ],
        }),
    ]
    inline_classes = ['grp-collapse', 'grp-closed']
    extra = 0
    model = CountrySubdivision
    verbose_name = _('Subdivision')
    verbose_name_plural = _('Subdivisions')


class CountryAdmin(admin.EnableableMixin, admin.ModelAdmin):

    change_list_filter_template = 'admin/filter_listing.html'
    fieldsets = [
        (None, {
            'fields': [
                'name',
                'code',
                'long_code',
                'number',
                'is_enabled',
                'region',
            ],
        }),
        (_('Localized Names'), {
            'classes': [
                'grp-collapse',
                'grp-closed',
            ],
            'fields': [
                'name_en',
                'name_fr',
                'name_es',
                'name_zh',
                'name_ru',
                'name_de',
                'name_pt',
            ],
        }),
    ]
    inlines = [CountrySubdivisionInline]
    list_display = [
        'name',
        'code',
        'long_code',
        'number',
    ]
    list_editable = [
        'code',
        'long_code',
        'number',
    ]
    list_filter = [
        'is_enabled',
        'region',
    ]
    search_fields = [
        'name',
        'code',
        'long_code',
        'number',
    ]


class CurrencyAdmin(admin.EnableableMixin, admin.ModelAdmin):

    change_list_filter_template = 'admin/filter_listing.html'
    fieldsets = [
        (None, {
            'fields': [
                'name',
                'symbol',
                'code',
                'number',
                'is_enabled',
            ],
        }),
        (_('Localized Names'), {
            'classes': [
                'grp-collapse',
                'grp-closed',
            ],
            'fields': [
                'name_en',
                'name_fr',
                'name_es',
                'name_zh',
                'name_ru',
                'name_de',
                'name_pt',
            ],
        }),
        (_('Additional Info'), {
            'classes': [
                'grp-collapse',
                'grp-closed',
            ],
            'fields': [
                'decimals',
                'countries',
            ],
        }),
    ]
    list_display = [
        'name',
        'symbol',
        'code',
        'number',
    ]
    list_editable = [
        'code',
        'number',
    ]
    list_filter = [
        'is_enabled',
    ]
    search_fields = [
        'name',
        'code',
        'number',
    ]


class LanguageAdmin(admin.EnableableMixin, admin.ModelAdmin):

    change_list_filter_template = 'admin/filter_listing.html'
    fieldsets = [
        (None, {
            'fields': [
                'name',
                'tag',
                'iso_639_1',
                'iso_639_2',
                'iso_639_3',
                'is_enabled',
            ],
        }),
        (_('Localized Names'), {
            'classes': [
                'grp-collapse',
                'grp-closed',
            ],
            'fields': [
                'name_en',
                'name_fr',
                'name_es',
                'name_zh',
                'name_ru',
                'name_de',
                'name_pt',
            ],
        }),
        (_('Additional Info'), {
            'classes': [
                'grp-collapse',
                'grp-closed',
            ],
            'fields': [
                'countries',
            ],
        }),
    ]
    list_display = [
        'name',
        'tag',
        'iso_639_1',
        'iso_639_2',
        'iso_639_3',
    ]
    list_editable = [
        'tag',
        'iso_639_1',
        'iso_639_2',
        'iso_639_3',
    ]
    list_filter = [
        'is_enabled',
    ]
    search_fields = [
        'name',
        'tag',
        'iso_639_1',
        'iso_639_2',
        'iso_639_3',
    ]


class RegionAdmin(admin.ModelAdmin):

    fieldsets = [
        (None, {
            'fields': [
                'name',
                'number',
                'parent',
            ],
        }),
        (_('Localized Names'), {
            'classes': [
                'grp-collapse',
                'grp-closed',
            ],
            'fields': [
                'name_en',
                'name_fr',
                'name_es',
                'name_zh',
                'name_ru',
                'name_de',
                'name_pt',
            ],
        }),
    ]
    list_display = [
        'name',
        'number',
    ]
    list_editable = [
        'number',
    ]
    search_fields = [
        'name',
        'number',
    ]


admin.site.register(Country, CountryAdmin)
admin.site.register(Currency, CurrencyAdmin)
admin.site.register(Language, LanguageAdmin)
admin.site.register(Region, RegionAdmin)
