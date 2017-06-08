# -*- coding:utf-8 -*-

from __future__ import division, unicode_literals

from collections import Iterable
from math import ceil

from django.core.exceptions import FieldDoesNotExist, ImproperlyConfigured
from django.db.models.query import QuerySet
from django.forms.models import modelform_factory
from django.http import Http404, HttpResponseRedirect
from django.utils import six
from django.utils.encoding import force_text, python_2_unicode_compatible
from django.utils.html import escape
from django.utils.safestring import mark_safe
from django.utils.six.moves import range
from django.utils.translation import ugettext as _
from django.views.generic import View
from django.views.generic.base import ContextMixin, TemplateResponseMixin
from django.views.generic.edit import FormMixin

from yepes.types import Undefined
from yepes.utils.properties import cached_property
from yepes.utils.structures import OrderedDictWhichIteratesOverValues
from yepes.view_mixins import CacheMixin, MessageMixin, ModelMixin


@python_2_unicode_compatible
class Ordering(object):

    name = Undefined
    fields = Undefined
    verbose_name = Undefined

    def __init__(self, query):
        assert self.name is not Undefined
        self._query = query
        if self.verbose_name is Undefined:
            self.verbose_name = force_text(self.name).capitalize()

    def __eq__(self, other):
        return (isinstance(other, Ordering) and self.name == other.name)

    def __hash__(self):
        return hash((self.__class__.__name__, self.name))

    def __ne__(self, other):
        return not self.__eq__(other)

    def __repr__(self):
        return str('<{0}: {1}>'.format(self.__class__.__name__, self.name))

    def __str__(self):
        return self.name

    def get_link(self):
        if self.is_selected:
            template = '<span class="selected">{verbose_name}</span>'
            kwargs = {
                'verbose_name': escape(self.verbose_name),
            }
        elif self.is_default:
            template = '<a href="{url}">{verbose_name}</a>'
            kwargs = {
                'url': escape(self.url),
                'verbose_name': escape(self.verbose_name),
            }
        else:
            template = '<a href="{url}" rel="nofollow">{verbose_name}</a>'
            kwargs = {
                'url': escape(self.url),
                'verbose_name': escape(self.verbose_name),
            }
        return mark_safe(template.format(**kwargs))

    def sort_objects(self, object_list):
        if self.fields is Undefined:
            msg = ('{cls} is missing a list of fields. Define {cls}.fields, '
                   'or override {cls}.sort_objects().')
            raise ImproperlyConfigured(msg.format(cls=self.__class__.__name__))
        else:
            return object_list.order_by(*self.fields)

    @cached_property
    def is_default(self):
        return (self._query.default_ordering == self)

    @cached_property
    def is_selected(self):
        return (self._query.ordering == self)

    @cached_property
    def url(self):
        return self._query.get_absolute_url(ordering=self, page=None)


@python_2_unicode_compatible
class Page(object):

    def __init__(self, query, value, verbose_name=None):
        assert isinstance(value, six.integer_types)
        self._query = query
        self.value = value
        if verbose_name is None:
            self.verbose_name = force_text(value)
        else:
            self.verbose_name = verbose_name

    def __eq__(self, other):
        return (isinstance(other, Page) and self.value == other.value)

    def __hash__(self):
        return hash((self.__class__.__name__, self.value))

    def __ne__(self, other):
        return not self.__eq__(other)

    def __repr__(self):
        return str('<{0}: {1}>'.format(self.__class__.__name__, self.value))

    def __str__(self):
        return force_text(self.value)

    def get_link(self):
        if self.value is None:
            template = '<span>{verbose_name}</span>'
            kwargs = {
                'verbose_name': escape(self.verbose_name),
            }
        elif self.is_selected:
            template = '<span class="selected">{verbose_name}</span>'
            kwargs = {
                'verbose_name': escape(self.verbose_name),
            }
        elif (self._query.ordering.is_default
                and self._query.page_size.is_default):
            template = '<a href="{url}">{verbose_name}</a>'
            kwargs = {
                'url': escape(self.url),
                'verbose_name': escape(self.verbose_name),
            }
        else:
            template = '<a href="{url}" rel="nofollow">{verbose_name}</a>'
            kwargs = {
                'url': escape(self.url),
                'verbose_name': escape(self.verbose_name),
            }
        return mark_safe(template.format(**kwargs))

    def limit_objects(self, object_list, page_size):
        if not page_size:
            return object_list

        start = (self.value - 1) * page_size.value
        if start > self._query.num_objects:
            return object_list[0:0]

        stop = start + page_size.value
        if stop + self._query.orphans > self._query.num_objects:
            stop = self._query.num_objects

        return object_list[start:stop]

    @cached_property
    def end_index(self):
        """
        Returns the 1-based index of the last object on this page,
        relative to total objects found (hits).
        """
        if self.value == self._query.num_pages:
            # Special case for the last page
            # because there can be orphans.
            return self._query.count
        else:
            return self.value * self._query.page_size.value

    @property
    def has_next(self):
        return self.next_page is not None

    @property
    def has_previous(self):
        return self.previous_page is not None

    @property
    def has_other_pages(self):
        return self.has_previous or self.has_next

    @cached_property
    def is_selected(self):
        return (self._query.page == self)

    @cached_property
    def next_page(self):
        return self._query.available_pages.get(self.value + 1)

    @property
    def next_page_number(self):
        return self.next_page.value if self.has_next else None

    @property
    def number(self):
        return self.value

    @cached_property
    def object_list(self):
        if not self._query.page_size:
            # If the pagination is not enabled, there is only one page
            # and it contains all the results of the query.
            return self._query.object_list
        else:
            return self._query.get_object_list(page=self)

    @cached_property
    def previous_page(self):
        return self._query.available_pages.get(self.value - 1)

    @property
    def previous_page_number(self):
        return self.previous_page.value if self.has_previous else None

    @cached_property
    def start_index(self):
        """
        Returns the 1-based index of the first object on this page,
        relative to total objects in the paginator.
        """
        if self._query.count == 0:
            # Special case, return zero if no items.
            return 0
        else:
            return (self._query.page_size.value * (self.value - 1)) + 1

    @cached_property
    def url(self):
        return self._query.get_absolute_url(page=self)


@python_2_unicode_compatible
class PageSize(object):

    value = Undefined
    verbose_name = Undefined

    def __init__(self, query):
        self._query = query
        assert self.value is not Undefined
        assert isinstance(self.value, six.integer_types)
        if self.verbose_name is Undefined:
            self.verbose_name = force_text(self.value)

    def __eq__(self, other):
        return (isinstance(other, PageSize) and self.value == other.value)

    def __hash__(self):
        return hash((self.__class__.__name__, self.value))

    def __ne__(self, other):
        return not self.__eq__(other)

    def __repr__(self):
        return str('<{0}: {1}>'.format(self.__class__.__name__, self.value))

    def __str__(self):
        return force_text(self.value)

    def get_link(self):
        if self.is_selected:
            template = '<span class="selected">{verbose_name}</span>'
            kwargs = {
                'verbose_name': escape(self.verbose_name),
            }
        elif self.is_default:
            template = '<a href="{url}">{verbose_name}</a>'
            kwargs = {
                'url': escape(self.url),
                'verbose_name': escape(self.verbose_name),
            }
        else:
            template = '<a href="{url}" rel="nofollow">{verbose_name}</a>'
            kwargs = {
                'url': escape(self.url),
                'verbose_name': escape(self.verbose_name),
            }
        return mark_safe(template.format(**kwargs))

    @cached_property
    def is_default(self):
        return (self._query.default_page_size == self)

    @cached_property
    def is_selected(self):
        return (self._query.page_size == self)

    @cached_property
    def url(self):
        return self._query.get_absolute_url(page=1, page_size=self)


class AvailablePages(object):

    def __init__(self, query):
        self._cache = {}
        self._query = query

    def __contains__(self, key):
        if key in self._cache:
            return True
        elif (isinstance(key, six.integer_types)
                and key >= 1
                and key <= self._query.num_pages):
            return True
        else:
            return False

    def __getitem__(self, key):
        if key in self._cache:
            return self._cache[key]
        elif (isinstance(key, six.integer_types)
                and key >= 1
                and key <= self._query.num_pages):
            self._cache[key] = page = Page(self._query, key)
            return page
        else:
            raise KeyError(key)

    def __iter__(self):
        return six.itervalues(self)

    def __len__(self):
        return self._query.num_pages

    def get(self, key, default=None):
        try:
            return self[key]
        except KeyError:
            return default

    if six.PY2:

        def items(self):
            return list(self.iteritems())

        def iteritems(self):
            for k in self.iterkeys():
                yield (k, self[k])

        def iterkeys(self):
            page = 1
            last_page = self._query.num_pages
            while page <= last_page:
                yield page
                page += 1

        def itervalues(self):
            for k in self.iterkeys():
                yield self[k]

        def keys(self):
            return list(self.iterkeys())

        def values(self):
            return list(self.itervalues())

    else:

        def items(self):
            for k in self.keys():
                yield (k, self[k])

        def keys(self):
            page = 1
            last_page = self._query.num_pages
            while page <= last_page:
                yield page
                page += 1

        def values(self):
            for k in self.keys():
                yield self[k]


class VisiblePages(object):

    def __init__(self, query, visible_pages=7):
        self._query = query

        start_page = query.page.value - ((visible_pages - 1) // 2)
        stop_page = query.page.value + int(round((visible_pages - 1) / 2))
        if start_page < 1:
            start_page = 1
            stop_page = visible_pages

        if stop_page > query.num_pages:
            start_page = start_page - stop_page + query.num_pages
            stop_page = query.num_pages
            if start_page < 1:
                start_page = 1

        self._range = list(range(start_page, stop_page + 1))

    def __contains__(self, key):
        if key in self._range:
            return True
        else:
            return False

    def __getitem__(self, key):
        if key in self._range:
            return self._query.available_pages[key]
        else:
            raise KeyError(key)

    def __iter__(self):
        return six.itervalues(self)

    def __len__(self):
        return len(self._range)

    def get(self, key, default=None):
        try:
            return self[key]
        except KeyError:
            return default

    if six.PY2:

        def items(self):
            return list(self.iteritems())

        def iteritems(self):
            for k in self.iterkeys():
                yield (k, self[k])

        def iterkeys(self):
            return iter(self._range)

        def itervalues(self):
            for k in self.iterkeys():
                yield self[k]

        def keys(self):
            return list(self.iterkeys())

        def values(self):
            return list(self.itervalues())

    else:

        def items(self):
            for k in self.keys():
                yield (k, self[k])

        def keys(self):
            return iter(self._range)

        def values(self):
            for k in self.keys():
                yield self[k]


class ListQuery(object):

    def __init__(self, view):
        self._view = view

    def __repr__(self):
        args = (
            self.__class__.__name__,
            self.get_query_string(page=self.page).replace('&', ' '),
        )
        return str('<{0} {1}>'.format(*args))

    def _limit_objects(self, object_list, page, page_size):
        page = self._prepare_page(page)
        page_size = self._prepare_page_size(page_size)
        if page and page_size and self.num_pages > 1:
            object_list = page.limit_objects(object_list, page_size)
        return object_list

    def _prepare_ordering(self, ordering):
        if ordering is Undefined:
            ordering = self.ordering
        elif ordering is not None and not isinstance(ordering, Ordering):
            ordering = self.available_orderings.get(ordering)
        return ordering

    def _prepare_page(self, page):
        if page is Undefined:
            page = None
        elif page is not None and not isinstance(page, Page):
            page = self.available_pages.get(page)
        return page

    def _prepare_page_size(self, page_size):
        if page_size is Undefined:
            page_size = self.page_size
        elif page_size is not None and not isinstance(page_size, PageSize):
            page_size = self.available_page_sizes.get(page_size)
        return page_size

    def _sort_objects(self, object_list, ordering):
        ordering = self._prepare_ordering(ordering)
        if ordering:
            object_list = ordering.sort_objects(object_list)
        return object_list

    def get_absolute_url(self, *args, **kwargs):
        path = self._view.request.path
        query = self.get_query_string(*args, **kwargs)
        if not query:
            return path
        else:
            return '?'.join((path, query))

    def get_object_list(self, ordering=Undefined, page=Undefined, page_size=Undefined):
        object_list = self.space
        object_list = self._sort_objects(object_list, ordering)
        object_list = self._limit_objects(object_list, page, page_size)
        return object_list

    def get_query_string(self, ordering=Undefined, page=Undefined, page_size=Undefined):
        ordering = self._prepare_ordering(ordering)
        page = self._prepare_page(page)
        page_size = self._prepare_page_size(page_size)

        params = []
        if ordering and ordering != self.default_ordering:
            params.append('{0}={1}'.format(self._ordering_kwarg, ordering))

        if page and page != self.first_page:
            params.append('{0}={1}'.format(self._page_kwarg, page))

        if page_size and page_size != self.default_page_size:
            params.append('{0}={1}'.format(self._page_size_kwarg, page_size))

        return '&'.join(params)

    @cached_property
    def _default_ordering(self):
        return self._view.get_default_ordering()

    @cached_property
    def _default_page_size(self):
        return self._view.get_default_page_size()

    @cached_property
    def _ordering(self):
        return self._view.get_selected_ordering()

    @cached_property
    def _ordering_kwarg(self):
        return self._view.ordering_kwarg

    @cached_property
    def _page(self):
        return self._view.get_selected_page()

    @cached_property
    def _page_kwarg(self):
        return self._view.page_kwarg

    @cached_property
    def _page_size(self):
        return self._view.get_selected_page_size()

    @cached_property
    def _page_size_kwarg(self):
        return self._view.page_size_kwarg

    @cached_property
    def available_orderings(self):
        orderings = OrderedDictWhichIteratesOverValues()
        for ordering_class in self._view.get_orderings():
            ordering = ordering_class(self)
            orderings[ordering.name] = ordering

        return orderings

    @cached_property
    def available_pages(self):
        return AvailablePages(self)

    @cached_property
    def available_page_sizes(self):
        sizes = OrderedDictWhichIteratesOverValues()
        for size_class in self._view.get_page_sizes():
            size = size_class(self)
            sizes[size.value] = size

        return sizes

    @property
    def count(self):
        return self.num_objects

    @cached_property
    def default_ordering(self):
        ordering = self.available_orderings.get(self._default_ordering)
        if not ordering:
            return next(iter(self.available_orderings), None)
        else:
            return ordering

    @cached_property
    def default_page_size(self):
        page_size = self.available_page_sizes.get(self._default_page_size)
        if not page_size:
            return next(iter(self.available_page_sizes), None)
        else:
            return page_size

    @cached_property
    def first_page(self):
        return self.available_pages.get(1)

    @cached_property
    def last_page(self):
        return self.available_pages.get(self.num_pages)

    @cached_property
    def num_objects(self):
        if not self.page_size:
            # If the pagination is not enabled, the object_list is probably
            # small. Therefore, it is better to do a single query, since the
            # object_list surely is going to be used.
            return len(self.object_list)
        else:
            try:
                return self.object_list.count()
            except (AttributeError, TypeError):
                # AttributeError if self.object_list has no count() method.
                # TypeError if self.object_list.count() requires arguments
                # (i.e. is of type list).
                return len(self.object_list)

    @cached_property
    def num_pages(self):
        if not self.page_size:
            return 1
        else:
            num_objects = max(1, self.num_objects - self.orphans)
            return int(ceil(num_objects / self.page_size.value))

    @cached_property
    def object_list(self):
        return self.get_object_list(page=None)

    @cached_property
    def ordering(self):
        selected_ordering = self.available_orderings.get(self._ordering)
        return selected_ordering or self.default_ordering

    @cached_property
    def orphans(self):
        return self._view.get_orphans()

    @cached_property
    def page(self):
        selected_page = self.available_pages.get(self._page)
        return selected_page or self.first_page

    @cached_property
    def page_size(self):
        selected_page_size = self.available_page_sizes.get(self._page_size)
        return selected_page_size or self.default_page_size

    @cached_property
    def space(self):
        return self._view.get_queryset()

    @cached_property
    def url(self):
        return self.get_absolute_url()

    @cached_property
    def visible_pages(self):
        return VisiblePages(self, self._view.get_visible_pages())


class ListView(CacheMixin, ContextMixin, ModelMixin, TemplateResponseMixin, View):
    """
    Render some list of objects, set by `self.model` or `self.queryset`.
    `self.queryset` can actually be any iterable of items, not just a queryset.
    """

    allow_empty = True
    context_object_name = None
    default_ordering = None
    default_page_size = None
    model = None
    ordering = None
    ordering_kwarg = 'ordering'
    _orderings = Undefined
    orphans = 0
    page_kwarg = 'page'
    page_size = None
    page_size_kwarg = 'page_size'
    _page_sizes = Undefined
    query_class = ListQuery
    queryset = None
    template_name_suffix = '_list'
    visible_pages = 7

    def dispatch(self, request, *args, **kwargs):
        self.query = self.get_query()
        self.object_list = self.query.object_list
        return super(ListView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        if not self.get_allow_empty() and self.query.num_objects == 0:
            msg = _("Empty list and '{class_name}.allow_empty' is False.")
            raise Http404(msg.format(class_name=self.__class__.__name__))
        context = self.get_context_data()
        return self.render_to_response(context)

    def get_allow_empty(self):
        """
        Returns ``True`` if the view should display empty lists, and ``False``
        if a 404 should be raised instead.
        """
        return self.allow_empty

    def get_cache_hash(self, request):
        return '?'.join((
            super(ListView, self).get_cache_hash(request),
            self.query.get_query_string(page=self.query.page),
        ))

    def get_context_data(self, **kwargs):
        """
        Gets the context for this view.
        """
        query = kwargs.pop('query', self.query)
        page = query.page
        queryset = page.object_list
        is_paginated = query.num_pages > 1

        context = {
            'query': query,
            'page_obj': page,
            'object_list': queryset,
            'is_paginated': is_paginated,
        }
        context_object_name = self.get_context_object_name(queryset)
        if context_object_name is not None:
            context[context_object_name] = queryset

        context.update(kwargs)
        return super(ListView, self).get_context_data(**context)

    def get_context_object_name(self, object_list):
        """
        Gets the name of the item to be used in the context.
        """
        if self.context_object_name:
            return self.context_object_name
        elif hasattr(object_list, 'model'):
            return '{0}_list'.format(object_list.model._meta.model_name)
        else:
            return None

    def get_default_ordering(self):
        """
        Returns the ordering to use when the user has not selected any.
        """
        return self.default_ordering

    def get_default_page_size(self):
        """
        Returns the page size to use when the user has not selected any.
        """
        return self.default_page_size

    def get_orderings(self):
        """
        Returns a list containing all available orderings.
        """
        if self._orderings is Undefined:
            self._orderings = self.normalize_orderings(self.ordering)
        return self._orderings

    def get_orphans(self):
        """
        Returns the maximum number of orphans extend the last page by when
        paginating.
        """
        return self.orphans

    def get_page_sizes(self):
        """
        Returns a list containing all available page sizes.
        """
        if self._page_sizes is Undefined:
            self._page_sizes = self.normalize_page_sizes(self.page_size)
        return self._page_sizes

    def get_query(self):
        """
        Returns an instance of the query for this view.
        """
        return self.query_class(self)

    def get_queryset(self):
        """
        Returns the space for quering the objects.

        The return value must be an iterable and may be an instance of
        `QuerySet`.

        """
        if self.queryset is not None:
            queryset = self.queryset
            if isinstance(queryset, QuerySet):
                queryset = queryset.all()
        elif self.model is not None:
            queryset = self.model._default_manager.all()
        else:
            msg = ('{cls} is missing a QuerySet. Define {cls}.model, '
                   '{cls}.queryset, or override {cls}.get_queryset().')
            raise ImproperlyConfigured(msg.format(cls=self.__class__.__name__))

        return queryset

    def get_selected_ordering(self):
        """
        Returns the ordering which the user has selected.
        """
        return self.request.GET.get(self.ordering_kwarg)

    def get_selected_page(self):
        """
        Returns the page which the user has selected.
        """
        page = self.request.GET.get(self.page_kwarg)
        try:
            return int(page)
        except (ValueError, TypeError):
            if page == 'last':
                return self.query.num_pages
            else:
                return None

    def get_selected_page_size(self):
        """
        Returns the page size which the user has selected.
        """
        size = self.request.GET.get(self.page_size_kwarg)
        try:
            return int(size)
        except (ValueError, TypeError):
            return None

    def get_template_names(self):
        """
        Returns a list of template names to be used for the request. Must
        return a list. May not be called if render_to_response is overridden.
        """
        try:
            names = super(ListView, self).get_template_names()
        except ImproperlyConfigured:
            # If template_name isn't specified, it's not a problem --
            # we just start with an empty list.
            names = []

        # If the list is a queryset, we'll invent a template name based on the
        # app and model name. This name gets put at the end of the template
        # name list so that user-supplied names override the automatically-
        # generated ones.
        model = self.get_model()
        if model is not None:
            names.append('{0}/{1}{2}.html'.format(
                         model._meta.app_label,
                         model._meta.model_name,
                         self.template_name_suffix))
        return names

    def get_visible_pages(self):
        """
        Returns the maximum number of pages to render in the pagination block.
        """
        return self.visible_pages

    def normalize_orderings(self, orderings):
        """
        Normalizes ``orderings`` to a list of subclasses of ``Ordering``.

        ``orderings`` can be a string, a tuple of strings, a subclass of
        ``Ordering``, or a list with any combination of above.

        """
        if not orderings:
            return []

        if (not isinstance(orderings, Iterable)
                or isinstance(orderings, (six.string_types, tuple))):
            orderings = [orderings]
        else:
            orderings = list(orderings)

        model = self.get_model()
        for i, ordering in enumerate(orderings):
            if not isinstance(ordering, type):

                if isinstance(ordering, six.string_types):
                    ordering_fields = [ordering]
                    ordering_name = ordering
                elif isinstance(ordering, tuple):
                    ordering_fields = list(ordering)
                    ordering_name = ordering_fields[0]
                else:
                    msg = ('{cls}.ordering should contain subclasses of'
                           ' Ordering, or strings or tuples with ordering data.')
                    raise ImproperlyConfigured(msg.format(cls=self.__class__.__name__))

                if ordering_name.startswith('-'):
                    ordering_name = '{0}_desc'.format(ordering_name[1:])

                attrs = {
                    'name': ordering_name,
                    'fields': ordering_fields,
                }
                if model is not None:
                    try:
                        field = model._meta.get_field(ordering_name)
                    except FieldDoesNotExist:
                        pass
                    else:
                        attrs['verbose_name'] = field.verbose_name

                orderings[i] = type(str('Ordering'), (Ordering, ), attrs)

        ordering_names = set()
        for ordering in orderings:
            if ordering.name in ordering_names:
                msg = 'Ordering with this name already exists: {0}'
                raise ImproperlyConfigured(msg.format(ordering.name))
            else:
                ordering_names.add(ordering.name)

        return orderings

    def normalize_page_sizes(self, sizes):
        """
        Normalizes ``sizes`` to a list of subclasses of ``PageSize``.

        ``sizes`` can be an integer, a subclass of ``PageSize``, or a list
        with any combination of both.

        """
        if not sizes:
            return []

        if isinstance(sizes, Iterable):
            sizes = list(sizes)
        else:
            sizes = [sizes]

        for i, size in enumerate(sizes):
            if not isinstance(size, type):
                try:
                    size = int(size)
                except (ValueError, TypeError):
                    msg = ('{cls}.page_size should contain subclasses of '
                           'PageSize or integer numbers.')
                    raise ImproperlyConfigured(msg.format(cls=self.__class__.__name__))
                else:
                    sizes[i] = type(str('Size'), (PageSize, ), {'value': size})

        return sizes


class ListAndCreateView(FormMixin, MessageMixin, ListView):

    object = None

    def form_valid(self, form):
        self.object = form.save()
        url = self.get_success_url()
        if not url:
            form = self.get_form(force_empty=True)
            context = self.get_context_data(create_form=form)
            response = self.render_to_response(context)
        else:
            response = HttpResponseRedirect(url)

        self.send_success_message(self.request)
        return response

    def form_invalid(self, form):
        context = self.get_context_data(create_form=form)
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super(ListAndCreateView, self).get_context_data(**kwargs)
        if 'create_form' not in context:
            context['create_form'] = self.get_form()
        return context

    def get_form(self, form_class=None, force_empty=False):
        if form_class is None:
            form_class = self.get_form_class()
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

    def get_success_url(self):
        return self.success_url

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def put(self, *args, **kwargs):
        return self.post(*args, **kwargs)

