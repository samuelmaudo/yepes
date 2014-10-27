# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from functools import update_wrapper
import hashlib

from django.conf.urls import patterns, url
from django.contrib.admin import ModelAdmin as DjangoModelAdmin
from django.contrib.admin.util import flatten_fieldsets, model_format_dict
from django.db import models
from django.db import transaction
from django.db.models.fields import BLANK_CHOICE_DASH, FieldDoesNotExist
from django.utils import six
from django.utils.encoding import smart_bytes

from yepes.admin import (
    actions as yepes_actions,
    operations as yepes_operations,
)
from yepes.admin.views import MassUpdateView


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

        if self.has_massupdate_permission(request):
            actions['mass_update'] = (
                yepes_actions.mass_update,
                'mass_update',
                yepes_actions.mass_update.short_description,
            )

        return actions

    def get_field_operations(self, request, field):
        operations = [yepes_operations.Set]
        if not field.choices and field.rel is None:
            if field.null:
                operations.append(
                    yepes_operations.SetNull,
                )
            if isinstance(field, models.CharField):
                operations.extend([
                    yepes_operations.Lower,
                    yepes_operations.Upper,
                    yepes_operations.Capitalize,
                    yepes_operations.Title,
                    yepes_operations.SwapCase,
                    yepes_operations.Strip,
                ])
            elif isinstance(field, (models.IntegerField,
                                    models.FloatField,
                                    models.DecimalField)):
                operations.extend([
                    yepes_operations.Add,
                    yepes_operations.Sub,
                    yepes_operations.Mul,
                    yepes_operations.Div,
                ])
            elif isinstance(field, (models.BooleanField,
                                    models.NullBooleanField)):
                operations.append(
                    yepes_operations.Swap,
                )
        return operations

    def get_formfields(self, request, unique=False, many_to_many=False, **kwargs):
        field_names = flatten_fieldsets(self.get_fieldsets(request))
        readonly_fields = self.get_readonly_fields(request)
        opts = self.opts
        db_fields = []
        for field_name in field_names:
            if field_name in readonly_fields:
                continue
            try:
                field = opts.get_field(
                    field_name,
                    many_to_many=many_to_many,
                )
            except FieldDoesNotExist:
                continue

            if not field.editable or (field.unique and not unique):
                continue

            db_fields.append(field)

        form_fields = []
        for dbfield in db_fields:
            formfield = self.formfield_for_dbfield(
                dbfield,
                request=request,
                **kwargs
            )
            if formfield is None:
                continue

            form_fields.append((dbfield, formfield))

        return form_fields

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

    def get_urls(self):

        def wrap(view):
            def wrapper(*args, **kwargs):
                return self.admin_site.admin_view(view)(*args, **kwargs)
            return update_wrapper(wrapper, view)

        info = (self.model._meta.app_label, self.model._meta.model_name)
        urls = patterns('',
            url(r'^mass-update/$',
                wrap(MassUpdateView.as_view(model_admin=self)),
                name='{0}_{1}_massupdate'.format(*info),
            ),
        )
        return urls + super(ModelAdmin, self).get_urls()

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

    def has_massupdate_permission(self, request, obj=None):
        return request.user.has_perm('mass_update')

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

    def update_queryset(self, request, queryset, ops, in_bulk=False):
        if not in_bulk:
            affected_rows = 0
            with transaction.atomic():
                for obj in queryset:
                    for op in ops:
                        op.run(obj)

                    obj.full_clean()
                    obj.save()
                    affected_rows += 1

            return affected_rows
        else:
            return queryset.update(**{
                op.field_name: op.as_expression()
                for op
                in ops
            })

