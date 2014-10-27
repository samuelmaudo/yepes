# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from django.contrib import messages
from django.contrib.admin import helpers
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _
from django.views.decorators.csrf import csrf_protect
from django.views.generic import FormView

from yepes.admin.forms import MassUpdateFormSet, MassUpdateErrorList
from yepes.views import decorate_view


TRUE_VALUES = ('on', 'yes', 'true', '1')


@decorate_view(
    csrf_protect,
)
class MassUpdateView(FormView):

    form_class = MassUpdateFormSet
    model_admin = None

    def dispatch(self, request, *args, **kwargs):
        if not self.model_admin.has_massupdate_permission(request):
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
                qs,
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

