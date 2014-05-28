# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from functools import wraps
import logging
import sys

from django.contrib.admin.views.decorators import staff_member_required
from django.core.cache import cache
from django.core.cache.backends.memcached import BaseMemcachedCache
from django.core.exceptions import ImproperlyConfigured, ObjectDoesNotExist
from django.core.urlresolvers import reverse_lazy
from django.forms.models import modelform_factory
from django.http import (
    Http404,
    HttpResponse,
    HttpResponseRedirect,
)
from django.utils import six
from django.utils.itercompat import is_iterable
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.generic.base import (
    TemplateResponseMixin,
    TemplateView,
)
from django.views.generic.detail import (
    BaseDetailView,
    SingleObjectTemplateResponseMixin,
)
from django.views.generic.edit import (
    BaseCreateView,
    BaseDeleteView,
    BaseFormView,
    BaseUpdateView,
    FormMixin,
)
from django.views.generic.list import (
    BaseListView,
    MultipleObjectTemplateResponseMixin,
)

from yepes.view_mixins import (
    CacheMixin,
    CanonicalMixin,
    MessageMixin,
    ModelMixin,
)
from yepes.types import Undefined

__all__ = (
    'decorate_view',
    'CacheMixin', 'CanonicalMixin', 'MessageMixin', 'ModelMixin',
    'DetailView',
    'FormView', 'CreateView', 'UpdateView', 'DeleteView',
    'ListView', 'ListAndCreateView',
    'CacheStatsView',
    'CachedTemplateView',
    'CsrfFailureView',
)

logger = logging.getLogger('django.request')


def decorate_view(*decorator_list):

    decorator_list = tuple(reversed(decorator_list))

    def class_decorator(cls):

        _dispatch = cls.dispatch
        def dispatch_wrapper(self, *args, **kwargs):
            def internal_wrapper(*args2, **kwargs2):
                return _dispatch(self, *args2, **kwargs2)
            for decorator in decorator_list:
                internal_wrapper = decorator(internal_wrapper)
            return internal_wrapper(*args, **kwargs)

        cls.dispatch = wraps(_dispatch)(dispatch_wrapper)
        return cls

    return class_decorator


@decorate_view(
    csrf_protect,
    never_cache,
    staff_member_required,
)
class CacheStatsView(TemplateView):

    template_name = 'cache/stats.html'
    url = reverse_lazy('cache_stats')

    def get_context_data(self, **kwargs):
        context = super(CacheStatsView, self).get_context_data(**kwargs)
        context.update({
            'title': _('Cache Stats'),
            'cache_timeout': cache.default_timeout,
            'cache_backend': cache.__class__.__name__[:-5],
        })
        if isinstance(cache, BaseMemcachedCache) and cache._cache.get_stats():
            stats = cache._cache.get_stats()[0][1]
            hits = float(stats['get_hits'])
            calls = float(stats['cmd_get'])
            used = float(stats['bytes'])
            total = float(stats['limit_maxbytes'])
            context.update({
                'cache_items': stats['curr_items'],
                'cache_size': stats['limit_maxbytes'],
                'cache_used': stats['bytes'],
                'cache_used_rate': '{:.2%}'.format(used / total),
                'cache_calls': stats['cmd_get'],
                'cache_hits': stats['get_hits'],
                'cache_hit_rate': '{:.2%}'.format(hits / calls),
                'cache_misses': stats['get_misses'],
            })
        return context

    def post(self, *args, **kwargs):
        cache.clear()
        return HttpResponseRedirect(self.url)

    def put(self, *args, **kwargs):
        return self.post(*args, **kwargs)


class CachedTemplateView(CacheMixin, TemplateView):
    pass


class CreateView(SingleObjectTemplateResponseMixin,
                 ModelMixin, MessageMixin, BaseCreateView):

    template_name_suffix = '_form'

    def form_valid(self, *args, **kwargs):
        response = super(CreateView, self).form_valid(*args, **kwargs)
        self.send_success_message(self.request)
        return response


class CsrfFailureView(TemplateView):

    template_name = 'csrf.html'

    def get(self, request, *args, **kwargs):
        # A CSRF failure is not strictly an error
        # but we want to log it as if it were.
        logger.error('CSRF Failure: %s', request.path,
            exc_info=sys.exc_info(),
            extra={
                'status_code': 403,
                'request': request,
            }
        )
        return super(CsrfFailureView, self).get(request, *args, **kwargs)

    def post(self, *args, **kwargs):
        return self.get(*args, **kwargs)

    def put(self, *args, **kwargs):
        return self.get(*args, **kwargs)

csrf_failure_view = CsrfFailureView.as_view()


class DeleteView(SingleObjectTemplateResponseMixin,
                 ModelMixin, MessageMixin, BaseDeleteView):

    template_name_suffix = '_form'

    def delete(self, *args, **kwargs):
        response = super(DeleteView, self).delete(*args, **kwargs)
        self.send_success_message(self.request)
        return response


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


class FormView(TemplateResponseMixin, ModelMixin, MessageMixin, BaseFormView):

    def form_valid(self, *args, **kwargs):
        response = super(FormView, self).form_valid(*args, **kwargs)
        self.send_success_message(self.request)
        return response


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
        return self.paginate_by

    def get_page_number(self):
        return (self.kwargs.get(self.page_kwarg)
                or self.request.GET.get(self.page_kwarg)
                or 1)

    def get_page_size(self):
        return (self.kwargs.get('paginate_by')
                or self.kwargs.get('page_size')
                or self.request.GET.get('paginate_by')
                or self.request.GET.get('page_size'))

    def get_paginate_by(self, queryset=None):
        """
        Get the number of items to paginate by, or ``None`` for no pagination.
        """
        if self._paginate_by is Undefined:
            allowed_sizes = self.get_allowed_page_sizes()
            if allowed_sizes is None:
                self._paginate_by = None
            else:

                if is_iterable(allowed_sizes):
                    allowed_sizes = [int(size) for size in allowed_sizes]
                else:
                    allowed_sizes [int(allowed_sizes)]

                page_size = self.get_page_size()
                page_size = int(page_size) if page_size else None
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


class UpdateView(SingleObjectTemplateResponseMixin,
                 ModelMixin, MessageMixin, BaseUpdateView):

    template_name_suffix = '_form'

    def form_valid(self, *args, **kwargs):
        response = super(UpdateView, self).form_valid(*args, **kwargs)
        self.send_success_message(self.request)
        return response

