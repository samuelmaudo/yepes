# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _

from yepes import admin
from yepes.loading import get_model

Country = get_model('standards', 'Country')
CountrySubdivision = get_model('standards', 'CountrySubdivision')
Currency = get_model('standards', 'Currency')
GeographicArea = get_model('standards', 'GeographicArea')
Language = get_model('standards', 'Language')
Region = get_model('standards', 'Region')


class CountrySubdivisionAdmin(admin.EnableableMixin, admin.ModelAdmin):

    autocomplete_lookup_fields = {
        'fk':  ['country'],
        'm2m': [],
    }
    fieldsets = [
        (None, {
            'fields': [
                'country',
                'name',
                'code',
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
    ]
    list_display = [
        'name',
        'code',
    ]
    list_editable = [
        'code',
    ]
    list_filter = [
        'is_enabled',
    ]
    raw_id_fields = [
        'country',
    ]
    search_fields = [
        'name',
        'code',
    ]


class CountrySubdivisionInline(admin.StackedInline):

    classes = ['grp-collapse', 'grp-closed']
    fieldsets = [
        (None, {
            'fields': [
                'is_enabled',
                'name',
                'code',
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
    inline_classes = ['grp-collapse', 'grp-closed']
    extra = 0
    model = CountrySubdivision
    verbose_name = _('Subdivision')
    verbose_name_plural = _('Subdivisions')


class CountryAdmin(admin.EnableableMixin, admin.ModelAdmin):

    autocomplete_lookup_fields = {
        'fk':  ['region'],
        'm2m': [],
    }
    fieldsets = [
        (None, {
            'fields': [
                'region',
                'name',
                'code',
                'long_code',
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
    raw_id_fields = [
        'region',
    ]
    search_fields = [
        'name',
        'code',
        'long_code',
        'number',
    ]


class CurrencyAdmin(admin.EnableableMixin, admin.ModelAdmin):

    autocomplete_lookup_fields = {
        'fk':  [],
        'm2m': ['countries'],
    }
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
    raw_id_fields = [
        'countries',
    ]
    search_fields = [
        'name',
        'code',
        'number',
    ]


class GeographicAreaAdmin(admin.ModelAdmin):

    autocomplete_lookup_fields = {
        'fk':  [],
        'm2m': [
            'excluded_countries', 'included_countries',
            'excluded_subdivisions', 'included_subdivisions',
        ],
    }
    fieldsets = [
        (None, {
            'fields': [
                'name',
                'api_id',
                'description',
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
        (_('Countries'), {
            'classes': [
                'grp-collapse',
                'grp-closed',
            ],
            'fields': [
                'included_countries',
                'excluded_countries',
            ],
        }),
        (_('Country Subdivisions'), {
            'classes': [
                'grp-collapse',
                'grp-closed',
            ],
            'fields': [
                'included_subdivisions',
                'excluded_subdivisions',
            ],
        }),
    ]
    list_display = [
        'name',
        'api_id',
        'includes_all_addresses',
    ]
    ordering = [
        'name',
    ]
    raw_id_fields = [
        'excluded_countries',
        'excluded_subdivisions',
        'included_countries',
        'included_subdivisions',
    ]
    search_fields = [
        'name',
        'api_id',
    ]


class LanguageAdmin(admin.EnableableMixin, admin.ModelAdmin):

    autocomplete_lookup_fields = {
        'fk':  [],
        'm2m': ['countries'],
    }
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
    raw_id_fields = [
        'countries',
    ]
    search_fields = [
        'name',
        'tag',
        'iso_639_1',
        'iso_639_2',
        'iso_639_3',
    ]


class RegionAdmin(admin.ModelAdmin):

    autocomplete_lookup_fields = {
        'fk':  ['parent'],
        'm2m': [],
    }
    fieldsets = [
        (None, {
            'fields': [
                'parent',
                'name',
                'number',
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
    raw_id_fields = [
        'parent',
    ]
    search_fields = [
        'name',
        'number',
    ]


admin.site.register(Country, CountryAdmin)
admin.site.register(CountrySubdivision, CountrySubdivisionAdmin)
admin.site.register(Currency, CurrencyAdmin)
admin.site.register(GeographicArea, GeographicAreaAdmin)
admin.site.register(Language, LanguageAdmin)
admin.site.register(Region, RegionAdmin)
