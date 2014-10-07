# -*- coding:utf-8 -*-

from __future__ import unicode_literals

import hashlib

from django import forms
from django.contrib.admin import (
    ModelAdmin as DjangoModelAdmin, HORIZONTAL, VERTICAL,
    StackedInline, TabularInline,
    AdminSite, site,
    ListFilter, SimpleListFilter, FieldListFilter, BooleanFieldListFilter,
    RelatedFieldListFilter, ChoicesFieldListFilter, DateFieldListFilter,
    AllValuesFieldListFilter,
)
from django.contrib.admin.actions import delete_selected
from django.contrib.admin.util import (
    flatten_fieldsets,
    get_model_from_relation,
    model_format_dict,
)
from django.db.models import F, Q
from django.db.models.fields import BLANK_CHOICE_DASH
from django.db.models.related import RelatedObject
from django.template.response import SimpleTemplateResponse
from django.utils import timezone
from django.utils import six
from django.utils.encoding import smart_bytes, smart_text
from django.utils.html import format_html
from django.utils.translation import ugettext_lazy as _


from yepes.model_mixins import (
    Activatable,
    Displayable,
    Enableable,
    Nestable,
)

__all__ = (
    'ModelAdmin',
    'HORIZONTAL', 'VERTICAL',
    'StackedInline', 'TabularInline',
    'AdminSite', 'site',
    'ListFilter', 'SimpleListFilter', 'FieldListFilter',
    'BooleanFieldListFilter', 'RelatedFieldListFilter',
    'ChoicesFieldListFilter', 'DateFieldListFilter',
    'AllValuesFieldListFilter', 'NestableFieldListFilter',
    'ActivatableMixin', 'DisplayableMixin', 'EnableableMixin',
    'IllustratedMixin', 'OrderableMixim', 'ReadOnlyMixin',
)

delete_selected.short_description = _('Delete selected {verbose_name_plural}')


class ModelAdmin(DjangoModelAdmin):

    def get_action_choices(self, request, default_choices=BLANK_CHOICE_DASH):
        # Change the string formatting operation to the ``str.format()`` method.
        choices = [] + default_choices
        model_verbose_names = model_format_dict(self.opts)
        for func, name, description in six.itervalues(self.get_actions(request)):
            choice = (name, description.format(**model_verbose_names))
            choices.append(choice)

        return choices

    def get_actions(self, request):
        # Move admin site actions to the end.
        actions = super(ModelAdmin, self).get_actions(request)
        if actions:
            for name, func in self.admin_site.actions:
                info = actions.pop(name)
                if (name != 'delete_selected'
                        or self.has_delete_permission(request)):
                    actions[name] = info

        return actions

    def get_inline_instances(self, request, obj=None):
        sup = super(ModelAdmin, self)
        inline_instances = sup.get_inline_instances(request, obj)
        if not self.has_change_permission(request, obj, strict=True):
            for inline in inline_instances:
                if inline.declared_fieldsets:
                    fields = flatten_fieldsets(inline.declared_fieldsets)
                else:
                    fields = {f.name for f in inline.model._meta.fields}
                    fields.update(inline.readonly_fields)

                inline.max_num = 0
                inline.readonly_fields = list(fields)

        return inline_instances

    def get_readonly_fields(self, request, obj=None):
        if self.has_change_permission(request, obj, strict=True):
            return self.readonly_fields

        if self.declared_fieldsets:
            fields = flatten_fieldsets(self.declared_fieldsets)
        else:
            fields = {f.name for f in self.model._meta.fields}
            fields.update(self.readonly_fields)

        return list(fields)

    # NOTE: Permission verification is an inexpensive task most of time.
    # However, I store permissions in cache because, if they change during
    # response process, they may cause problems.

    def _get_cache_attribute(self, view, obj):
        h = hashlib.md5(smart_bytes('{0}.{1}.{2}'.format(
                self.opts.app_label,
                self.opts.object_name.lower(),
                hash(obj))))
        return '_{0}_permission_{1}'.format(view, h.hexdigest())

    def has_add_permission(self, request):
        attr_name = self._get_cache_attribute('add', None)
        try:
            permission = getattr(request, attr_name)
        except AttributeError:
            permission = self._has_add_permission(request)
            setattr(request, attr_name, permission)

        return permission

    def _has_add_permission(self, request):
        app_label = self.opts.app_label
        add_permission = self.opts.get_add_permission()
        return request.user.has_perm(app_label + '.' + add_permission)

    def has_change_permission(self, request, obj=None, strict=False):
        if not strict:
            return self.has_view_permission(request, obj)

        attr_name = self._get_cache_attribute('change', obj)
        try:
            permission = getattr(request, attr_name)
        except AttributeError:
            permission = self._has_change_permission(request, obj)
            setattr(request, attr_name, permission)

        return permission

    def _has_change_permission(self, request, obj):
        app_label = self.opts.app_label
        change_permission = self.opts.get_change_permission()
        return request.user.has_perm(app_label + '.' + change_permission)

    def has_delete_permission(self, request, obj=None):
        attr_name = self._get_cache_attribute('delete', obj)
        try:
            permission = getattr(request, attr_name)
        except AttributeError:
            permission = self._has_delete_permission(request, obj)
            setattr(request, attr_name, permission)

        return permission

    def _has_delete_permission(self, request, obj):
        app_label = self.opts.app_label
        delete_permission = self.opts.get_delete_permission()
        return request.user.has_perm(app_label + '.' + delete_permission)

    def has_view_permission(self, request, obj=None):
        attr_name = self._get_cache_attribute('view', obj)
        try:
            permission = getattr(request, attr_name)
        except AttributeError:
            permission = self._has_view_permission(request, obj)
            setattr(request, attr_name, permission)

        return permission

    def _has_view_permission(self, request, obj):
        #app_label = self.opts.app_label
        #view_permission = self.opts.get_view_permission()
        #return request.user.has_perm(app_label + '.' + view_permission)
        return True

    def report_change(self, request, queryset, affected_rows,
                      log_message, user_message, user_message_plural):
        kwargs = model_format_dict(self.opts)
        for obj in queryset:
            self.log_change(request, obj, log_message.format(record=obj, **kwargs))

        if affected_rows == 1:
            kwargs['record'] = queryset.get()
            self.message_user(request, user_message.format(**kwargs))
        else:
            kwargs['record_count'] = affected_rows
            self.message_user(request, user_message_plural.format(**kwargs))



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


class NestableFieldListFilter(FieldListFilter):

    level_indicator = '– '

    def __init__(self, field, request, params, model, model_admin, field_path):
        self.lookup_kwarg = '{0}__in'.format(field_path)
        self.lookup_kwarg_isnull = '{0}__isnull'.format(field_path)
        self.lookup_val = request.GET.get(self.lookup_kwarg)
        self.lookup_val_isnull = request.GET.get(self.lookup_kwarg_isnull)
        self.other_model = get_model_from_relation(field)
        opts = self.other_model._mptt_meta
        qs = self.other_model._default_manager
        if self.other_model is model:
            qs = qs.filter(**{
                '{0}__gt'.format(opts.right_attr): F(opts.left_attr) + 1,
            })
        self.objects = qs.order_by(opts.tree_id_attr, opts.left_attr)
        super(NestableFieldListFilter, self).__init__(field, request, params, model, model_admin, field_path)

    def choices(self, cl):
        yield {
            'selected': self.lookup_val is None and not self.lookup_val_isnull,
            'query_string': cl.get_query_string({},
                [self.lookup_kwarg, self.lookup_kwarg_isnull]),
            'display': _('All'),
        }
        if ((isinstance(self.field, RelatedObject) and self.field.field.null)
                    or (hasattr(self.field, 'rel') and self.field.null)):
            yield {
                'selected': bool(self.lookup_val_isnull),
                'query_string': cl.get_query_string({
                    self.lookup_kwarg_isnull: 'True',
                }, [self.lookup_kwarg]),
                'display': _('None'),
            }
        for obj in self.objects:
            yield {
                'selected': self.lookup_val == smart_text(obj.pk),
                'query_string': cl.get_query_string({
                    self.lookup_kwarg: smart_text(obj.pk),
                }, [self.lookup_kwarg_isnull]),
                'display': self.label(obj),
            }

    def expected_parameters(self):
        return [self.lookup_kwarg, self.lookup_kwarg_isnull]

    def has_output(self):
        choices_count = len(self.objects)
        if ((isinstance(self.field, RelatedObject) and self.field.field.null)
                    or (hasattr(self.field, 'rel') and self.field.null)):
            choices_count += 1
        return choices_count > 1

    def label(self, obj):
        return '{0} {1}'.format(
                self.level_indicator * obj.get_level_number(),
                smart_text(obj))

    def queryset(self, request, queryset):
        if self.lookup_val_isnull:
            return queryset.filter(**{self.lookup_kwarg_isnull: True})
        elif self.lookup_val is not None:
            obj = self.other_model._default_manager.get(pk=self.lookup_val)
            objects = obj.get_descendants(include_self=True)
            return queryset.filter(**{self.lookup_kwarg: objects})

FieldListFilter.register(
    lambda f: (
        bool(getattr(f, 'rel', None))
            and issubclass(f.rel.to, Nestable)
        or
        isinstance(f, RelatedObject)
            and issubclass(f.field.rel.to, Nestable)
    ),
    NestableFieldListFilter,
    take_priority=True,
)


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

