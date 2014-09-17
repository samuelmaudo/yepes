# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from django.views.generic.base import TemplateResponseMixin
from django.views.generic.detail import SingleObjectTemplateResponseMixin
from django.views.generic.edit import (
    BaseCreateView,
    BaseDeleteView,
    BaseFormView,
    BaseUpdateView,
)

from yepes.view_mixins import MessageMixin, ModelMixin


class CreateView(SingleObjectTemplateResponseMixin,
                 ModelMixin, MessageMixin, BaseCreateView):

    template_name_suffix = '_form'

    def form_valid(self, *args, **kwargs):
        response = super(CreateView, self).form_valid(*args, **kwargs)
        self.send_success_message(self.request)
        return response


class DeleteView(SingleObjectTemplateResponseMixin,
                 ModelMixin, MessageMixin, BaseDeleteView):

    template_name_suffix = '_form'

    def delete(self, *args, **kwargs):
        response = super(DeleteView, self).delete(*args, **kwargs)
        self.send_success_message(self.request)
        return response


class FormView(TemplateResponseMixin, ModelMixin, MessageMixin, BaseFormView):

    def form_valid(self, *args, **kwargs):
        response = super(FormView, self).form_valid(*args, **kwargs)
        self.send_success_message(self.request)
        return response


class UpdateView(SingleObjectTemplateResponseMixin,
                 ModelMixin, MessageMixin, BaseUpdateView):

    template_name_suffix = '_form'

    def form_valid(self, *args, **kwargs):
        response = super(UpdateView, self).form_valid(*args, **kwargs)
        self.send_success_message(self.request)
        return response

