# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from django.contrib.contenttypes.models import ContentType
from django.http import Http404, HttpResponse
from django.utils import six
from django.utils.itercompat import is_iterable
from django.utils.translation import ugettext as _
from django.views.generic.detail import (
    BaseDetailView,
    SingleObjectTemplateResponseMixin,
)

from yepes.loading import is_installed, LazyModelManager
from yepes.view_mixins import CacheMixin, CanonicalMixin, ModelMixin
from yepes.types import Undefined

SlugHistoryManager = LazyModelManager('slugs', 'SlugHistory')


class DetailView(SingleObjectTemplateResponseMixin,
                 CacheMixin, CanonicalMixin, ModelMixin, BaseDetailView):
    """
    Render a 'detail' view of an object.

    By default this is a model instance looked up from ``self.queryset``,
    but the view will support display of *any* object by overriding
    ``self.get_object()``.

    """
    _object = Undefined
    view_signal = None

    def dispatch(self, *args, **kwargs):
        response = super(DetailView, self).dispatch(*args, **kwargs)
        if (isinstance(response, HttpResponse)
                and response.status_code == 200
                and not self.request.user.is_staff):
            self.send_view_signal(self.get_object(), self.request, response)
        return response

    def get_object(self, queryset=None):
        """
        Returns the object the view is displaying.

        By default this requires ``self.queryset`` and a ``pk`` or ``slug``
        argument in the URLconf, but subclasses can override this to return
        any object.

        """
        if self._object is Undefined:
            try:
                obj = super(DetailView, self).get_object(queryset)
            except Http404 as e:
                if not is_installed('slugs'):
                    raise e

                #if queryset is None:
                    #model = self.get_model()
                #else:
                    #model = queryset.model

                #object_id = self.kwargs.get(self.pk_url_kwarg, None)
                #object_type = ContentType.objects.get_for_model(model)
                #slug = self.kwargs.get(self.slug_url_kwarg, None)

                #queryset = SlugHistoryManager.select_related('object')
                #queryset = queryset.filter(slug=slug)
                #queryset = queryset.filter(object_type=object_type)
                #if object_id is not None:
                    #queryset = queryset.filter(object_id=object_id)

                #records = list(queryset[:1])
                #if not records:
                    #raise e

                #obj = records[0].object

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

            self._object = obj

        return self._object

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

    def send_view_signal(self, obj, request, response):
        if self.view_signal is not None:
            self.view_signal.send(
                sender=self,
                obj=obj,
                request=request,
                response=response)

