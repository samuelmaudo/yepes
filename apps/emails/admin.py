# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from django import forms
from django.db import models
from django.utils.translation import ugettext_lazy as _

from yepes import admin
from yepes.loading import get_model

Connection = get_model('emails', 'Connection')
Delivery = get_model('emails', 'Delivery')
Message = get_model('emails', 'Message')


class ConnectionAdmin(admin.ModelAdmin):

    change_list_template = 'admin/change_list_filter_sidebar.html'
    change_list_filter_template = 'admin/filter_listing.html'
    fieldsets = [
        (None, {
            'fields': [
                'name',
            ],
        }),
        (_('Settings'), {
            'fields': [
                'host',
                'port',
                'username',
                'password',
                'is_secure',
                'is_logged',
            ]
        }),
    ]
    list_display = [
        'name',
        'host',
        'username',
        'is_secure',
        'is_logged',
    ]
    list_filter = [
        'is_secure',
        'is_logged',
    ]
    search_fields = [
        'name',
        'host',
    ]


class DeliveryAdmin(admin.ModelAdmin):

    date_hierarchy = 'date'
    fieldsets = [
        (None, {
            'fields': [
                'subject',
                'date',
                'sender',
                'recipients',
                'other_recipients',
                'hidden_recipients',
            ],
        }),
        (_('Body'), {
            'classes': [
                'grp-collapse',
                'grp-closed',
            ],
            'fields': [
                'html',
                'text',
            ]
        }),
    ]
    list_display = [
        'subject',
        'recipients',
        'date',
    ]
    search_fields = [
        'subject',
        'sender',
        'recipients',
    ]
    readonly_fields = ['date']

    def _has_add_permission(self, request):
        return False
    def _has_change_permission(self, request, obj):
        return False
    def _has_delete_permission(self, request, obj):
        return False


class MessageAdmin(admin.ModelAdmin):

    fieldsets = [
        (None, {
            'fields': [
                'name',
                'subject',
                'html',
                'text',
            ],
        }),
        (_('Settings'), {
            'classes': [
                'grp-collapse',
                'grp-closed',
            ],
            'fields': [
                'connection',
                'sender_name',
                'sender_address',
                'recipient_name',
                'recipient_address',
                'reply_to_name',
                'reply_to_address',
            ]
        }),
    ]
    formfield_overrides = {
        models.TextField: {'widget': forms.Textarea(attrs={'style': 'height:290px'})},
    }
    list_display = [
        'name',
        'subject',
        'sender',
        'recipient',
    ]
    search_fields = [
        'name',
        'subject',
    ]


admin.site.register(Connection, ConnectionAdmin)
admin.site.register(Delivery, DeliveryAdmin)
admin.site.register(Message, MessageAdmin)
