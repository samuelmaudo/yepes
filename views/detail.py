# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404, HttpResponse
from django.utils import six
from django.utils.itercompat import is_iterable
from django.utils.translation import ugettext_lazy as _
from django.views.generic.detail import (
    BaseDetailView,
    SingleObjectTemplateResponseMixin,
)

from yepes.view_mixins import CacheMixin, CanonicalMixin, ModelMixin
from yepes.types import Undefined


class DetailView(SingleObjectTemplateResponseMixin,
                 CacheMixin, CanonicalMixin, ModelMixin, BaseDetailView):
    """
    Render a 'detail' view of an object.

    By default this is a model instance looked up from ``self.queryset``,
    but the view will support display of *any* object by overriding
    ``self.get_object()``.

    """
    _object = Undefined
    guid_field = 'guid'
    guid_url_kwarg = 'guid'
    view_signal = None

    def dispatch(self, *args, **kwargs):
        response = super(DetailView, self).dispatch(*args, **kwargs)
        if (isinstance(response, HttpResponse)
                and response.status_code in (200, 404)
                and not self.request.user.is_staff):
            self.send_view_signal(self.get_object(), self.request, response)
        return response

    def get_guid_field(self):
        """
        Get the name of a guid field to be used to look up by guid.
        """
        return self.guid_field

    def get_object(self, queryset=None):
        """
        Returns the object the view is displaying.

        By default this requires ``self.queryset`` and a ``pk``, ``guid`` or
        ``slug`` argument in the URLconf, but subclasses can override this to
        return any object.

        """
        if self._object is not Undefined:
            return self._object

        # Use a custom queryset if provided; this is required for subclasses
        # like DateDetailView
        if queryset is None:
            queryset = self.get_queryset()

        pk = self.kwargs.get(self.pk_url_kwarg, None)
        guid = self.kwargs.get(self.guid_url_kwarg, None)
        slug = self.kwargs.get(self.slug_url_kwarg, None)

        # Next, try looking up by primary key.
        if pk is not None:
            queryset = queryset.filter(pk=pk)

        # Next, try looking up by guid.
        elif guid is not None:
            guid_field = self.get_guid_field()
            queryset = queryset.filter(**{guid_field: guid})

        # Next, try looking up by slug.
        elif slug is not None:
            slug_field = self.get_slug_field()
            queryset = queryset.filter(**{slug_field: slug})

        # If none of those are defined, it's an error.
        else:
            msg = ('Generic detail view {0} must be called with either an'
                   ' object pk or a guid or a slug.')
            raise AttributeError(msg.format(self.__class__.__name__))

        # Get the single item from the filtered queryset
        try:
            self._object = queryset.get()
        except ObjectDoesNotExist:
            opts = queryset.model._meta
            msg = _('No {verbose_name} found matching the query')
            raise Http404(msg.format(verbose_name=opts.verbose_name))

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

