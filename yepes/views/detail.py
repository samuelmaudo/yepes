# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from django.http import Http404, HttpResponse
from django.utils import six
from django.utils.itercompat import is_iterable
from django.views.generic.detail import (
    BaseDetailView,
    SingleObjectTemplateResponseMixin,
)

from yepes.apps import apps
from yepes.view_mixins import CacheMixin, CanonicalMixin, ModelMixin
from yepes.utils.properties import cached_property


class DetailView(SingleObjectTemplateResponseMixin, CacheMixin,
                 CanonicalMixin, ModelMixin, BaseDetailView):
    """
    Render a 'detail' view of an object.

    By default this is a instance of ``self.model``, but the view will
    support display of *any* object by overriding ``self.get_object()``.

    It differs from ``django.views.generic.DetailView`` in that includes
    ``CacheMixin``, ``CanonicalMixin`` and ``ModelMixin``. Further,
    ``self.object`` is a cached property, so it is set the first time it
    is get.

    """
    view_signal = None

    def dispatch(self, *args, **kwargs):
        response = super(DetailView, self).dispatch(*args, **kwargs)
        if isinstance(response, HttpResponse) and response.status_code == 200:

            try:
                is_staff = self.request.user.is_staff
            except AttributeError:
                is_staff = False

            if is_staff:
                self.send_view_signal(self.object, self.request, response)

        return response

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)

    def get_canonical_path(self, request):
        """
        Returns the canonical path to compare it with the requested path.

        By default this uses the object ``get_absolute_url()`` method but
        subclasses can override this to calculate the canonical path in any
        other way.

        """
        return self.object.get_absolute_url()

    def get_object(self, queryset=None):
        """
        Returns the object the view is displaying.

        By default this requires ``self.queryset`` and a ``pk`` or ``slug``
        argument in the URLconf, but subclasses can override this to return
        any object.

        """
        try:
            obj = super(DetailView, self).get_object(queryset)
        except Http404 as e:
            if 'slugs' not in apps:
                raise e

            pk = self.kwargs.get(self.pk_url_kwarg, None)
            slug = self.kwargs.get(self.slug_url_kwarg, None)
            if slug is None:
                raise e

            if queryset is None:
                queryset = self.get_queryset()

            queryset = queryset.order_by('-slug_history__id')
            queryset = queryset.filter(slug_history__slug=slug)
            if pk is not None:
                queryset = queryset.filter(slug_history__object_id=pk)

            records = list(queryset[:1])
            if not records:
                raise e

            obj = records[0]

        return obj

    def get_template_names(self):
        """
        Returns a list of template names to be used for the request. May
        not be called if render_to_response is overridden.
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

    def send_view_signal(self, obj, request, response):
        """
        If ``self.view_signal`` is set, sends it.
        """
        if self.view_signal is not None:
            self.view_signal.send(
                sender=self,
                obj=obj,
                request=request,
                response=response)

    @cached_property
    def object(self):
        return self.get_object()

