# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from django.core.exceptions import ImproperlyConfigured
from django.forms.models import modelform_factory
from django.http import Http404, HttpResponseRedirect
from django.utils import six
from django.utils.itercompat import is_iterable
from django.utils.translation import ugettext_lazy as _
from django.views.generic.base import TemplateResponseMixin
from django.views.generic.edit import FormMixin
from django.views.generic.list import (
    BaseListView,
    MultipleObjectTemplateResponseMixin,
)

from yepes.view_mixins import CacheMixin, MessageMixin, ModelMixin
from yepes.types import Undefined


class ListView(MultipleObjectTemplateResponseMixin,
               CacheMixin, ModelMixin, BaseListView):
    """
    Render some list of objects, set by ``self.model`` or ``self.queryset``.

    NOTE: ``self.queryset`` can actually be any iterable of items, not just a
    queryset.

    """
    _paginate_by = Undefined

    def get_cache_hash(self, request):
        uri = super(ListView, self).get_cache_hash(request)
        if self.get_paginate_by():
            uri += '?page={0}'.format(self.get_page_number())
            uri += '&page_size={0}'.format(self.get_paginate_by())
        return uri

    def get_context_data(self, **kwargs):
        context = super(ListView, self).get_context_data(**kwargs)
        page = context['page_obj']
        paginator = context['paginator']
        context['page_number'] = page.number if page else 1
        context['page_size'] = paginator.per_page if paginator else None
        return context

    def get_allowed_page_sizes(self):
        if self.paginate_by is None:
            return []
        elif is_iterable(self.paginate_by):
            return [int(size) for size in self.paginate_by]
        else:
            return [int(self.paginate_by)]

    def get_page_number(self):
        return int(self.kwargs.get(self.page_kwarg)
                   or self.request.GET.get(self.page_kwarg)
                   or 1)

    def get_page_size(self):
        return int(self.kwargs.get('paginate_by')
                   or self.kwargs.get('page_size')
                   or self.request.GET.get('paginate_by')
                   or self.request.GET.get('page_size')
                   or 0)

    def get_paginate_by(self, queryset=None):
        """
        Get the number of items to paginate by, or ``None`` for no pagination.
        """
        if self._paginate_by is Undefined:
            allowed_sizes = self.get_allowed_page_sizes()
            if not allowed_sizes:
                self._paginate_by = None
            else:
                page_size = self.get_page_size()
                if page_size and page_size in allowed_sizes:
                    self._paginate_by = page_size
                else:
                    self._paginate_by = allowed_sizes[0]

        return self._paginate_by

    def get_template_names(self):
        """
        Returns a list of template names to be used for the request.
        """
        names = []
        if isinstance(self.template_name, six.string_types):
            names.append(self.template_name)
        elif is_iterable(self.template_name):
            names.extend(self.template_name)

        model = self.get_model()
        if model is not None:
            args = (
                model._meta.app_label,
                model._meta.model_name,
                self.template_name_suffix,
            )
            names.append('{0}/{1}{2}.html'.format(*args))

        return names


class ListAndCreateView(ListView, ModelMixin, MessageMixin, FormMixin):

    object = None

    def form_valid(self, form):
        self.object = form.save()
        url = self.get_success_url()
        if not url:
            form_class = self.get_form_class()
            form = self.get_form(form_class, force_empty=True)
            context = self.get_context_data(create_form=form)
            response = self.render_to_response(context)
        else:
            response = HttpResponseRedirect(url)
        self.send_success_message(self.request)
        return response

    def form_invalid(self, form):
        context = self.get_context_data(create_form=form)
        return self.render_to_response(context)

    def get(self, request, *args, **kwargs):
        self.object_list = self.get_object_list()
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        context = self.get_context_data(create_form=form)
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = {'object_list': self.object_list}
        context.update(kwargs)
        return super(ListAndCreateView, self).get_context_data(**context)

    def get_form(self, form_class, force_empty=False):
        return form_class(**self.get_form_kwargs(force_empty=force_empty))

    def get_form_class(self):
        if self.form_class:
            return self.form_class

        model = self.get_model()
        if model is not None:
            return modelform_factory(model)

        msg = "'{0}' must define 'form_class', 'queryset' or 'model'"
        raise ImproperlyConfigured(msg.format(self.__class__.__name__))

    def get_form_kwargs(self, force_empty=False):
        kwargs = {'initial': self.get_initial()}
        if not force_empty and self.request.method in ('POST', 'PUT'):
            kwargs.update({
                'data': self.request.POST,
                'files': self.request.FILES,
            })
        return kwargs

    def get_object_list(self, **kwargs):
        object_list = self.get_queryset()
        allow_empty = self.get_allow_empty()

        if not allow_empty:
            # When pagination is enabled and object_list is a queryset,
            # it's better to do a cheap query than to load the unpaginated
            # queryset in memory.
            if (self.get_paginate_by(object_list) is not None
                    and hasattr(object_list, 'exists')):
                is_empty = (not object_list.exists())
            else:
                is_empty = (len(object_list) == 0)
            if is_empty:
                msg = _("Empty list and '{class_name}.allow_empty' is False.")
                raise Http404(msg.format(class_name=self.__class__.__name__))

        return object_list

    def get_success_url(self):
        return self.success_url

    def post(self, request, *args, **kwargs):
        self.object_list = self.get_object_list()
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def put(self, *args, **kwargs):
        return self.post(*args, **kwargs)

