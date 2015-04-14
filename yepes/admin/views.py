# -*- coding:utf-8 -*-

from __future__ import unicode_literals

import datetime
import decimal
import json
import tablib

from django.contrib import messages
from django.contrib.admin import helpers
from django.core import files
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.db import models
from django.http import HttpResponse
from django.utils.translation import ugettext as _
from django.views.decorators.csrf import csrf_protect
from django.views.generic import FormView, View

from yepes.admin.forms import MassUpdateFormSet, MassUpdateErrorList
from yepes.utils.views import decorate_view


TRUE_VALUES = ('on', 'yes', 'true', '1')


@decorate_view(
    csrf_protect,
)
class ExportView(View):

    model_admin = None

    def dispatch(self, request, *args, **kwargs):
        model_admin = self.get_model_admin()
        if (model_admin is None
                or not model_admin.has_export_permission(request)):
            raise PermissionDenied
        else:
            return super(ExportView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        data = tablib.Dataset(*self.get_data(), headers=self.get_headers())
        return HttpResponse(data.yaml, content_type='application/json; charset=utf-8')

    def get_data(self):
        fields = self.get_fields()
        return [
            tuple(self.get_prep_value(obj, fld) for fld in fields)
            for obj
            in self.get_queryset()
        ]

    def get_fields(self):
        model_admin = self.get_model_admin()
        opts = model_admin.model._meta
        return opts.fields

    def get_headers(self):
        return [fld.name for fld in self.get_fields()]

    def get_model_admin(self):
        return self.model_admin

    def get_queryset(self):
        qs = self.get_model_admin().get_queryset(self.request)
        ids = self.request.GET.get('ids')
        if ids:
            qs = qs.filter(pk__in=ids.split(','))

        return qs

    def get_prep_value(self, obj, field):
        value = field.get_prep_value(
                    field.value_from_object(obj))

        if isinstance(value, datetime.datetime):
            v = value.isoformat()
            if value.microsecond:
                v = v[:23] + v[26:]
            if v.endswith('+00:00'):
                v = v[:-6] + 'Z'
            return v

        elif isinstance(value, datetime.date):
            return value.isoformat()

        elif isinstance(value, datetime.time):
            v = value.isoformat()
            if value.microsecond:
                v = v[:12] + v[15:]
            if v.endswith('+00.00'):
                v = v[:-6] + ['Z']
            return v

        elif isinstance(value, decimal.Decimal):
            v = str(value)
            if '.' not in v:
                return int(v)

            """
            I did the following test and I found that is safe to convert
            decimals in floats and vice versa if you take care of convert
            the float in a string before converting it into a decimal.

            >>> import sys
            >>> try:
            ...     import cdecimal
            ... except ImportError:
            ...     pass
            ... else:
            ...     sys.modules['decimal'] = cdecimal
            ...
            >>> from decimal import Decimal as dec
            ...
            >>> def test(max_digits, decimal_places):
            ...     error_count = 0
            ...     for i in range(10 ** max_digits):
            ...         s = str(i)
            ...         if len(s) < decimal_places:
            ...             s = ('0' * (decimal_places - len(s))) + s
            ...         s = '.'.join((s[:-decimal_places], s[-decimal_places:]))
            ...         if dec(s) != dec(str(float(dec(s)))):
            ...             error_count += 1
            ...     print 'Errors:', error_count
            ...
            >>> test(18, 6)
            Errors: 0

            WARNING: This test takes a long long time, at least in my computer.

            """
            integer, decimals = v.split('.', 1)
            decimals = decimals.rstrip('0')
            if not decimals:
                return int(integer)
            elif len(decimals) <= 6 and len(integer) + len(decimals) <= 18:
                return float(v)
            else:
                return '.'.join((integer, decimals))

        elif isinstance(value, files.File):
            return value.name
        else:
            return value


@decorate_view(
    csrf_protect,
)
class ImportView(View):

    model_admin = None

    def dispatch(self, request, *args, **kwargs):
        model_admin = self.get_model_admin()
        if (model_admin is None
                or not model_admin.has_import_permission(request)):
            raise PermissionDenied
        else:
            return super(ImportView, self).dispatch(request, *args, **kwargs)

    def get_model_admin(self):
        return self.model_admin

    def get_queryset(self):
        qs = self.get_model_admin().get_queryset(self.request)
        ids = self.request.GET.get('ids')
        if ids:
            qs = qs.filter(pk__in=ids.split(','))

        return qs


@decorate_view(
    csrf_protect,
)
class MassUpdateView(FormView):

    form_class = MassUpdateFormSet
    model_admin = None

    def dispatch(self, request, *args, **kwargs):
        model_admin = self.get_model_admin()
        if (model_admin is None
                or not model_admin.has_massupdate_permission(request)):
            raise PermissionDenied
        else:
            return super(MassUpdateView, self).dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        model_admin = self.get_model_admin()
        opts = model_admin.model._meta

        ops = []
        for f in form:
            if f.cleaned_data['update']:
                op = f.cleaned_data['operation']
                if op.needs_value:
                    ops.append(op(f.field, f.cleaned_data['value']))
                else:
                    ops.append(op(f.field))

        if not ops:
            affected_rows = 0
            msg = _('No {verbose_name} was updated.')
            msg_level = messages.INFO
        elif self.request.POST.get('confirm_update') not in TRUE_VALUES:
            return self.render_to_response(self.get_context_data(
                form=form,
                operations=ops,
            ))
        else:
            qs = model_admin.get_queryset(self.request)
            ids = self.request.GET.get('ids')
            if ids:
                qs = qs.filter(pk__in=ids.split(','))

            affected_rows = model_admin.update_queryset(
                self.request,
                self.get_queryset(),
                ops,
                in_bulk=(self.request.POST.get('bulk_update') in TRUE_VALUES),
            )
            if not affected_rows:
                msg = _('No {verbose_name} was updated.')
                msg_level = messages.WARNING
            elif affected_rows == 1:
                msg = _('{record_count} {verbose_name} was updated successfully.')
                msg_level = messages.SUCCESS
            else:
                msg = _('{record_count} {verbose_name_plural} were updated successfully.')
                msg_level = messages.SUCCESS

        model_admin.message_user(
            self.request,
            msg.format(
                record_count=affected_rows,
                verbose_name=opts.verbose_name,
                verbose_name_plural=opts.verbose_name_plural,
            ),
            msg_level,
        )
        return super(MassUpdateView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(MassUpdateView, self).get_context_data(**kwargs)
        model_admin = self.get_model_admin()
        formset = context.pop('form')
        opts = model_admin.model._meta
        admin_form = helpers.AdminForm(
            formset,
            model_admin.get_fieldsets(self.request),
            {},
            model_admin.get_readonly_fields(self.request),
            model_admin,
        )
        context.update({
            'adminform': admin_form,
            'app_label': opts.app_label,
            'bulk_update': self.request.POST.get('bulk_update') in TRUE_VALUES,
            'errors': MassUpdateErrorList(formset),
            'media': formset.media,
            'opts': opts,
            'title': _('Mass update'),
        })
        return context

    def get_form_kwargs(self):
        kwargs = super(MassUpdateView, self).get_form_kwargs()
        kwargs['model_admin'] = self.get_model_admin()
        kwargs['request'] = self.request
        return kwargs

    def get_model_admin(self):
        return self.model_admin

    def get_queryset(self):
        qs = self.get_model_admin().get_queryset(self.request)
        ids = self.request.GET.get('ids')
        if ids:
            qs = qs.filter(pk__in=ids.split(','))

        return qs

    def get_success_url(self):
        model_admin = self.get_model_admin()
        opts = model_admin.model._meta
        url_name = 'admin:{0}_{1}_changelist'.format(
            opts.app_label,
            opts.model_name,
        )
        return reverse(url_name)

    def get_template_names(self):
        if self.template_name is None:
            model_admin = self.get_model_admin()
            opts = model_admin.model._meta
            return [
                'admin/{0}/{1}/mass_update.html'.format(opts.app_label, opts.model_name),
                'admin/{0}/mass_update.html'.format(opts.app_label),
                'admin/mass_update.html',
            ]
        else:
            return [self.template_name]

