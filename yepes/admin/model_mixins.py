# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from django import forms
from django.utils import timezone
from django.utils.html import format_html
from django.utils.translation import ugettext_lazy as _

from yepes.model_mixins import Activatable, Displayable, Enableable


class ActivatableMixin(object):

    actions = ['make_active', 'make_inactive']

    def admin_active_status(self, obj):
        pattern = '<span style="color:{0}">{1}</span>'
        if obj.is_active():
            color = '#42AD3F'
            text = _('Active')
        else:
            color = '#DE2121'
            text = _('Inactive')
        return format_html(pattern, color, text)
    admin_active_status.admin_order_field = 'active_status'
    admin_active_status.allow_tags = True
    admin_active_status.short_description = _('Status')

    def make_active(self, request, queryset):
        qs = queryset.all()
        qs.query.aggregates.clear()
        affected_rows = qs.update(active_status=Activatable.ACTIVE)
        qs.filter(active_from=None).update(active_from=timezone.now())
        self.report_change(
            request, qs, affected_rows,
            log_message=_('Activate "{record}"'),
            user_message=_('"{record}" has been successfully activated'),
            user_message_plural=_('{record_count} {verbose_name_plural} has been successfully activated'))
    make_active.short_description = _('Activate selected {verbose_name_plural}')

    def make_inactive(self, request, queryset):
        qs = queryset.all()
        qs.query.aggregates.clear()
        affected_rows = qs.update(active_status=Activatable.INACTIVE)
        self.report_change(
            request, qs, affected_rows,
            log_message=_('Deactivate "{record}"'),
            user_message=_('"{record}" has been successfully deactivated'),
            user_message_plural=_('{record_count} {verbose_name_plural} has been successfully deactivated'))
    make_inactive.short_description = _('Deactivate selected {verbose_name_plural}')


class DisplayableMixin(object):

    actions = ['make_published', 'make_hidden']

    def admin_publish_status(self, obj):
        pattern = '<span style="color:{0}">{1}</span>'
        if obj.is_draft():
            color = '#DE2121'
            text = _('Draft')
        elif obj.is_hidden():
            color = '#DE2121'
            text = _('Hidden')
        elif obj.is_published():
            color = '#42AD3F'
            text = _('Published')
        else:
            color = '#EE9A31'
            text = _('Not published')
        return format_html(pattern, color, text)
    admin_publish_status.admin_order_field = 'publish_status'
    admin_publish_status.allow_tags = True
    admin_publish_status.short_description = _('Status')

    def make_hidden(self, request, queryset):
        qs = queryset.all()
        qs.query.aggregates.clear()
        affected_rows = qs.update(publish_status=Displayable.HIDDEN)
        self.report_change(
            request, qs, affected_rows,
            log_message=_('Hide "{record}"'),
            user_message=_('"{record}" has been successfully hidden'),
            user_message_plural=_('{record_count} {verbose_name_plural} has been successfully hidden'))
    make_hidden.short_description = _('Hide selected {verbose_name_plural}')

    def make_published(self, request, queryset):
        qs = queryset.all()
        qs.query.aggregates.clear()
        affected_rows = qs.update(publish_status=Displayable.PUBLISHED)
        qs.filter(publish_from=None).update(publish_from=timezone.now())
        self.report_change(
            request, qs, affected_rows,
            log_message=_('Publish "{record}"'),
            user_message=_('"{record}" has been successfully published'),
            user_message_plural=_('{record_count} {verbose_name_plural} has been successfully published'))
    make_published.short_description = _('Publish selected {verbose_name_plural}')


class EnableableMixin(object):

    actions = ['make_enabled', 'make_disabled']

    def admin_enable_status(self, obj):
        pattern = '<span style="color:{0}">{1}</span>'
        if obj.is_enabled:
            color = '#42AD3F'
            text = _('Enabled')
        else:
            color = '#DE2121'
            text = _('Disabled')
        return format_html(pattern, color, text)
    admin_enable_status.admin_order_field = 'is_enabled'
    admin_enable_status.allow_tags = True
    admin_enable_status.short_description = _('Status')

    def make_disabled(self, request, queryset):
        qs = queryset.all()
        qs.query.aggregates.clear()
        affected_rows = qs.update(is_enabled=Enableable.DISABLED)
        self.report_change(
            request, qs, affected_rows,
            log_message=_('Disable "{record}"'),
            user_message=_('"{record}" has been successfully disabled'),
            user_message_plural=_('{record_count} {verbose_name_plural} has been successfully disabled'))
    make_disabled.short_description = _('Disable selected {verbose_name_plural}')

    def make_enabled(self, request, queryset):
        qs = queryset.all()
        qs.query.aggregates.clear()
        affected_rows = qs.update(is_enabled=Enableable.ENABLED)
        self.report_change(
            request, qs, affected_rows,
            log_message=_('Enable "{record}"'),
            user_message=_('"{record}" has been successfully enabled'),
            user_message_plural=_('{record_count} {verbose_name_plural} has been successfully enabled'))
    make_enabled.short_description = _('Enable selected {verbose_name_plural}')


class IllustratedMixin(object):

    image_field = 'image'

    def admin_image(self, obj):
        pattern = (
          '<img src="{0}" style="border-radius:3px;'
                               ' max-height:60px;'
                               ' max-width:60px">'
        )
        image = getattr(obj, self.image_field)
        return format_html(pattern, image.url)
    admin_image.allow_tags = True
    admin_image.short_description = _('Preview')


class OrderableForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(OrderableForm, self).__init__(*args, **kwargs)
        formfield = self.fields.get('index')
        formfield.label = ''
        formfield.widget = forms.TextInput(attrs={
            'style': 'display:none',
            'type': 'number',
        })


class OrderableMixim(object):
    form = OrderableForm
    sortable_field_name = 'index'


class ReadOnlyMixin(object):

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None, strict=False):
        return False if strict else self.has_view_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        return False

    def has_view_permission(self, request, obj=None):
        return True

