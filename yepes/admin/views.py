# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from tempfile import TemporaryFile
from wsgiref.util import FileWrapper

from django.contrib import messages
from django.contrib.admin import helpers
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.http import StreamingHttpResponse
from django.utils.translation import ugettext as _
from django.views.decorators.csrf import csrf_protect
from django.views.generic import FormView, View

from yepes.admin.forms import MassUpdateFormSet, MassUpdateErrorList
from yepes.admin.view_mixins import AdminMixin
from yepes.apps.data_migrations import QuerySetExportation
from yepes.utils.views import decorate_view


TRUE_VALUES = ('on', 'yes', 'true', '1')


@decorate_view(
    csrf_protect,
)
class CsvExportView(AdminMixin, View):

    content_type='text/csv; charset=utf-8'
    serializer_name = 'csv'

    def dispatch(self, request, *args, **kwargs):
        modeladmin = self.get_modeladmin()
        if (modeladmin is None
                or not modeladmin.has_view_permission(request)):
            raise PermissionDenied
        else:
            return super(CsvExportView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        qs = self.get_queryset()
        opts = qs.model._meta
        temp_file = TemporaryFile()
        migration = QuerySetExportation(qs)
        migration.export_data(temp_file, self.serializer_name)
        response = StreamingHttpResponse(
            FileWrapper(temp_file),
            content_type=self.content_type,
        )
        response['Content-Disposition'] = 'attachment; filename="{0}.{1}.{2}"'.format(
            opts.app_label,
            opts.object_name,
            self.serializer_name,
        )
        response['Content-Length'] = temp_file.tell()
        temp_file.seek(0)
        return response


class JsonExportView(CsvExportView):
    content_type='application/json; charset=utf-8'
    serializer_name = 'json'


class TsvExportView(CsvExportView):
    content_type='text/tab-separated-values; charset=utf-8'
    serializer_name = 'tsv'


class YamlExportView(CsvExportView):
    content_type='application/x-yaml; charset=utf-8'
    serializer_name = 'yaml'


@decorate_view(
    csrf_protect,
)
class MassUpdateView(AdminMixin, FormView):

    form_class = MassUpdateFormSet

    def dispatch(self, request, *args, **kwargs):
        modeladmin = self.get_modeladmin()
        if (modeladmin is None
                or not modeladmin.has_change_permission(request)):
            raise PermissionDenied
        else:
            return super(MassUpdateView, self).dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        modeladmin = self.get_modeladmin()
        opts = modeladmin.model._meta

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
            affected_rows = modeladmin.update_queryset(
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

        modeladmin.message_user(
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
        modeladmin = self.get_modeladmin()
        formset = context.pop('form')
        opts = modeladmin.model._meta
        admin_form = helpers.AdminForm(
            formset,
            modeladmin.get_fieldsets(self.request),
            {},
            modeladmin.get_readonly_fields(self.request),
            modeladmin,
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
        kwargs['modeladmin'] = self.get_modeladmin()
        kwargs['request'] = self.request
        return kwargs

    def get_success_url(self):
        modeladmin = self.get_modeladmin()
        opts = modeladmin.model._meta
        url_name = 'admin:{0}_{1}_changelist'.format(
            opts.app_label,
            opts.model_name,
        )
        return self.add_preserved_filters(reverse(url_name))

    def get_template_names(self):
        if self.template_name is None:
            modeladmin = self.get_modeladmin()
            opts = modeladmin.model._meta
            return [
                'admin/{0}/{1}/mass_update.html'.format(opts.app_label, opts.model_name),
                'admin/{0}/mass_update.html'.format(opts.app_label),
                'admin/mass_update.html',
            ]
        else:
            return [self.template_name]

