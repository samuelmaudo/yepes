# -*- coding:utf-8 -*-

from __future__ import division, unicode_literals

from collections import Iterable, OrderedDict
from math import ceil

from django.core.exceptions import ImproperlyConfigured
from django.db.models.query import QuerySet
from django.utils import six
from django.utils.encoding import force_text, python_2_unicode_compatible
from django.utils.html import escape
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _
from django.views.generic.base import ContextMixin, TemplateResponseMixin, View

from yepes.types import Undefined
from yepes.utils.http import urlquote_plus
from yepes.utils.properties import cached_property
from yepes.utils.structures import OrderedDictThatIteratesOverValues
from yepes.view_mixins import CacheMixin, ModelMixin


@python_2_unicode_compatible
class Filter(object):

    name = Undefined
    is_multiple = False
    verbose_name = Undefined

    def __init__(self, search):
        self._search = search
        assert self.name is not Undefined
        if self.verbose_name is Undefined:
            self.verbose_name = force_text(self.name).capitalize()

    def __eq__(self, other):
        return (isinstance(other, Filter) and self.name == other.name)

    def __hash__(self):
        return hash((self.__class__, self.name))

    def __ne__(self, other):
        return not self.__eq__(other)

    def __str__(self):
        return self.name

    def filter_results(self, results, options=Undefined):
        raise NotImplementedError('Subclasses of Filter must override filter_results() method')

    def get_all_options(self):
        raise NotImplementedError('Subclasses of Filter must override get_all_options() method')

    def get_options(self):
        raise NotImplementedError('Subclasses of Filter must override get_options() method')

    @cached_property
    def _options(self):
        return self._search._filters.get(self.name) or ()

    @cached_property
    def available_options(self):
        return OrderedDictThatIteratesOverValues([
            (option.name, option)
            for option
            in self.get_options()
        ])

    @cached_property
    def options(self):
        options = OrderedDictThatIteratesOverValues()
        for option in self.get_selected_options():
            options[option.name] = option
            if not self.is_multiple:
                break

        return options

    @cached_property
    def remove_url(self):
        filters = [
            f
            for f
            in self._search.filters
            if f != self
        ]
        return self._search.get_absolute_url(filters=filters, page=None)


@python_2_unicode_compatible
class FilterOption(object):

    def __init__(self, filter, value, name=None, verbose_name=None, count=None):
        self._search = filter._search
        self.filter = filter
        self.value = value
        if name is not None:
            self.name = force_text(name)
        else:
            self.name = force_text(value)

        if verbose_name is not None:
            self.verbose_name = force_text(verbose_name)
        else:
            self.verbose_name = self.name.capitalize()

        self.count = count

    def __eq__(self, other):
        return (isinstance(other, FilterOption)
                and self.filter == other.filter
                and self.name == other.name)

    def __hash__(self):
        return hash((self.__class__, self.filter, self.name))

    def __ne__(self, other):
        return not self.__eq__(other)

    def __str__(self):
        return self.name

    def get_link(self):
        if self.is_selected:
            template = '<a href="{remove_url}" class="selected" rel="nofollow">{verbose_name}</a>'
            kwargs = {
                'remove_url': escape(self.remove_url),
                'verbose_name': escape(self.verbose_name),
            }
        elif self.count is None:
            template = '<a href="{url}" rel="nofollow">{verbose_name}</a>'
            kwargs = {
                'url': escape(self.url),
                'verbose_name': escape(self.verbose_name),
            }
        else:
            template = '<a href="{url}" rel="nofollow">{verbose_name} <span class="count">({count})</span></a>'
            kwargs = {
                'count': self.count,
                'url': escape(self.url),
                'verbose_name': escape(self.verbose_name),
            }
        return mark_safe(template.format(**kwargs))

    @cached_property
    def is_selected(self):
        return (self.name in self.filter.options)

    @cached_property
    def remove_url(self):
        filters = [
            f
            for f
            in self._search.filters
            if f != self.filter
        ]
        if self.filter.is_multiple:
            options = [
                option
                for option
                in self.filter.options
                if option != self
            ]
            if options:
                filters.append((self.filter, options))

        return self._search.get_absolute_url(filters=filters, page=None)

    @cached_property
    def url(self):
        filters = [
            f
            for f
            in self._search.filters
            if f != self.filter
        ]
        if self.filter.is_multiple:
            options = [
                option
                for option
                in self.filter.options
                if option != self
            ]
            options.append(self)
            filters.append((self.filter, options))
        else:
            filters.append((self.filter, [self]))

        return self._search.get_absolute_url(filters=filters, page=None)


@python_2_unicode_compatible
class Ordering(object):

    name = Undefined
    fields = Undefined
    verbose_name = Undefined

    def __init__(self, search):
        self._search = search
        assert self.name is not Undefined
        if self.verbose_name is Undefined:
            self.verbose_name = force_text(self.name).capitalize()

    def __eq__(self, other):
        return (isinstance(other, Ordering) and self.name == other.name)

    def __hash__(self):
        return hash((self.__class__, self.name))

    def __ne__(self, other):
        return not self.__eq__(other)

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

    def order_results(self, results):
        if self.fields is Undefined:
            msg = ('{cls} is missing a list of fields. Define {cls}.fields, '
                   'or override {cls}.order_results().')
            raise ImproperlyConfigured(msg.format(cls=self.__class__.__name__))
        else:
            return results.order_by(*self.fields)

    @cached_property
    def is_default(self):
        return (self._search.default_ordering == self)

    @cached_property
    def is_selected(self):
        return (self._search.ordering == self)

    @cached_property
    def url(self):
        return self._search.get_absolute_url(ordering=self, page=None)


@python_2_unicode_compatible
class Page(object):

    def __init__(self, search, value, verbose_name=None):
        self._search = search
        assert isinstance(value, six.integer_types)
        self.value = value
        if verbose_name is None:
            self.verbose_name = force_text(value)
        else:
            self.verbose_name = verbose_name

    def __eq__(self, other):
        return (isinstance(other, Page) and self.value == other.value)

    def __hash__(self):
        return hash((self.__class__, self.value))

    def __ne__(self, other):
        return not self.__eq__(other)

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
        elif (self._search.ordering.is_default
                and self._search.page_size.is_default):
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
    def is_selected(self):
        return (self._search.page == self)

    @cached_property
    def next_page(self):
        return self._search.available_pages.get(self.value + 1)

    @cached_property
    def previous_page(self):
        return self._search.available_pages.get(self.value - 1)

    @cached_property
    def results(self):
        return self._search.get_results(page=self)

    @cached_property
    def url(self):
        return self._search.get_absolute_url(page=self)


@python_2_unicode_compatible
class PageSize(object):

    value = Undefined
    verbose_name = Undefined

    def __init__(self, search):
        self._search = search
        assert self.value is not Undefined
        assert isinstance(self.value, six.integer_types)
        if self.verbose_name is Undefined:
            self.verbose_name = force_text(self.value)

    def __eq__(self, other):
        return (isinstance(other, PageSize) and self.value == other.value)

    def __hash__(self):
        return hash((self.__class__, self.value))

    def __ne__(self, other):
        return not self.__eq__(other)

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
        return (self._search.default_page_size == self)

    @cached_property
    def is_selected(self):
        return (self._search.page_size == self)

    @cached_property
    def url(self):
        return self._search.get_absolute_url(page=1, page_size=self)


class SearchAvailablePages(object):

    def __init__(self, search):
        self._cache = {}
        self._search = search

    def __getitem__(self, key):
        if key in self._cache:
            return self._cache[key]
        elif (isinstance(key, six.integer_types)
                and key >= 1
                and key <= self._search.num_pages):
            self._cache[key] = page = Page(self._search, key)
            return page
        else:
            raise KeyError(key)

    def __iter__(self):
        return six.itervalues(self)

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
            last_page = self._search.num_pages
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
            last_page = self._search.num_pages
            while page <= last_page:
                yield page
                page += 1

        def values(self):
            for k in self.keys():
                yield self[k]


class SearchVisiblePages(object):

    def __init__(self, search, visible_pages=7):
        self._search = search

        start_page = search.page.value - ((visible_pages - 1) // 2)
        stop_page = search.page.value + int(round((visible_pages - 1) / 2))
        if start_page < 1:
            start_page = 1
            stop_page = visible_pages

        if stop_page > search.num_pages:
            start_page = start_page - stop_page + search.num_pages
            stop_page = search.num_pages
            if start_page < 1:
                start_page = 1

        self._range = list(range(start_page, stop_page + 1))

    def __getitem__(self, key):
        if key in self._range:
            return self._search.available_pages[key]
        else:
            raise KeyError(key)

    def __iter__(self):
        return six.itervalues(self)

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


class Search(object):

    def __init__(self, view):
        self._view = view

    def _prepare_parameters(self, user_query, filters, ordering, page, page_size):
        if user_query is Undefined:
            user_query = self.user_query

        if filters is Undefined:
            filters = self.filters

        if ordering is Undefined:
            ordering = self.ordering
        elif ordering is not None and not isinstance(ordering, Ordering):
            ordering = self.available_orderings.get(ordering)

        if page is Undefined:
            page = None
        elif page is not None and not isinstance(page, Page):
            page = self.available_pages.get(page)

        if page_size is Undefined:
            page_size = self.page_size
        elif page_size is not None and not isinstance(page_size, PageSize):
            page_size = self.available_page_sizes.get(page_size)

        return user_query, filters, ordering, page, page_size

    def get_absolute_url(self, user_query=Undefined, filters=Undefined,
                               ordering=Undefined, page=Undefined,
                               page_size=Undefined):
        path = self._view.request.path
        query = self.get_query_string(user_query, filters, ordering, page, page_size)
        if not query:
            return path
        else:
            return '?'.join((path, query))

    def get_query_string(self, user_query=Undefined, filters=Undefined,
                               ordering=Undefined, page=Undefined,
                               page_size=Undefined):

        user_query, filters, ordering, page, page_size = self._prepare_parameters(
                                   user_query, filters, ordering, page, page_size)

        params = []
        if user_query:
            params.append('{0}={1}'.format(
                self._user_query_kwarg,
                urlquote_plus(user_query, safe=''),
            ))

        if filters:
            filter_params = []
            for f in filters:
                if isinstance(f, Filter):
                    opts = f.options
                else:
                    f, opts = f

                filter_params.append('{0}:{1}'.format(f, ':'.join(opt.name for opt in opts)))

            params.append('{0}={1}'.format(self._filters_kwarg, ','.join(filter_params)))

        if ordering and ordering != self.default_ordering:
            params.append('{0}={1}'.format(self._ordering_kwarg, ordering))

        if page and page != self.first_page:
            params.append('{0}={1}'.format(self._page_kwarg, page))

        if page_size and page_size != self.default_page_size:
            params.append('{0}={1}'.format(self._page_size_kwarg, page_size))

        return '&'.join(params)

    def get_results(self, user_query=Undefined, filters=Undefined,
                          ordering=Undefined, page=Undefined,
                          page_size=Undefined):

        user_query, filters, ordering, page, page_size = self._prepare_parameters(
                                   user_query, filters, ordering, page, page_size)

        queryset = self.space
        if user_query:
            queryset = queryset.search(user_query)

        if filters:
            for f in filters:
                if isinstance(f, Filter):
                    queryset = f.filter_results(queryset)
                else:
                    filter, options = f
                    queryset = filter.filter_results(queryset, options)

        if ordering:
            queryset = ordering.order_results(queryset)

        if page and page_size:
            start = (page.value - 1) * page_size.value
            if start > self.num_results:
                return queryset.none()

            stop = start + page_size.value
            if stop > self.num_results:
                stop = self.num_results

            queryset = queryset[start:stop]

        return queryset

    @cached_property
    def _default_ordering(self):
        return self._view.get_default_ordering()

    @cached_property
    def _default_page_size(self):
        return self._view.get_default_page_size()

    @cached_property
    def _filters(self):
        return self._view.get_selected_filters()

    @cached_property
    def _filters_kwarg(self):
        return self._view.filters_kwarg

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
    def _user_query_kwarg(self):
        return self._view.user_query_kwarg

    @cached_property
    def available_filters(self):
        filters = OrderedDictThatIteratesOverValues()
        for filter_class in self._view.get_filters():
            filter = filter_class(self)
            filters[filter.name] = filter

        return filters

    @cached_property
    def available_orderings(self):
        orderings = OrderedDictThatIteratesOverValues()
        for ordering_class in self._view.get_orderings():
            ordering = ordering_class(self)
            orderings[ordering.name] = ordering

        if self.user_query:
            if all((len(ord.fields) != 1 or ord.fields[0] != 'search_score')
                   for ord
                   in orderings):
                attrs = {
                    'name': 'relevance',
                    'fields': ['search_score'],
                    'verbose_name': _('Relevance'),
                }
                ordering_class = type(str('Ordering'), (Ordering, ), attrs)
                orderings['relevance'] = ordering_class(self)

        return orderings

    @cached_property
    def available_pages(self):
        return SearchAvailablePages(self)

    @cached_property
    def available_page_sizes(self):
        sizes = OrderedDictThatIteratesOverValues()
        for size_class in self._view.get_page_sizes():
            size = size_class(self)
            sizes[size.value] = size

        return sizes

    @cached_property
    def default_ordering(self):
        ordering = self.available_orderings.get(self._default_ordering)
        if self.user_query:
            for ord in self.available_orderings:
                if 'search_score' in ord.fields:
                    ordering = ord
                    break

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
    def filters(self):
        selected_filters = OrderedDictThatIteratesOverValues()
        for name in self._filters:
            filter = self.available_filters.get(name)
            if filter is not None:
                selected_filters[filter.name] = filter

        return selected_filters

    @cached_property
    def first_page(self):
        return self.available_pages.get(1)

    @cached_property
    def last_page(self):
        return self.available_pages.get(self.num_pages)

    @cached_property
    def num_pages(self):
        return int(ceil(max(1, self.num_results) / self.page_size.value))

    @cached_property
    def num_results(self):
        try:
            return self.results.count()
        except (AttributeError, TypeError):
            # AttributeError if self.results has no count() method.
            # TypeError if self.results.count() requires arguments
            # (i.e. is of type list).
            return len(self.results)

    @cached_property
    def ordering(self):
        selected_ordering = self.available_orderings.get(self._ordering)
        return selected_ordering or self.default_ordering

    @cached_property
    def page(self):
        selected_page = self.available_pages.get(self._page)
        return selected_page or self.first_page

    @cached_property
    def page_size(self):
        selected_page_size = self.available_page_sizes.get(self._page_size)
        return selected_page_size or self.default_page_size

    @cached_property
    def results(self):
        return self.get_results(page=None)

    @cached_property
    def space(self):
        return self._view.get_queryset()

    @cached_property
    def url(self):
        return self.get_absolute_url()

    @cached_property
    def user_query(self):
        query = self._view.get_user_query()
        if query is None:
            return query
        else:
            return ' '.join(query.split())

    @cached_property
    def visible_pages(self):
        return SearchVisiblePages(self, self._view.get_visible_pages())


class SearchView(CacheMixin, ContextMixin, ModelMixin, TemplateResponseMixin, View):

    context_object_name = None
    default_ordering = None
    default_page_size = None
    filters = None
    _filters = Undefined
    filters_kwarg = 'filters'
    model = None
    ordering_kwarg = 'ordering'
    orderings = None
    _orderings = Undefined
    orphans = 0
    page_kwarg = 'page'
    page_size_kwarg = 'page_size'
    page_sizes = None
    _page_sizes = Undefined
    queryset = None
    search_class = Search
    template_name_suffix = '_search'
    user_can_query = False
    user_query_kwarg = 'query'
    visible_pages = 7

    def dispatch(self, request, *args, **kwargs):
        self.search = self.get_search()
        return super(SearchView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        context = self.get_context_data()
        return self.render_to_response(context)

    def get_cache_hash(self, request):
        return '?'.join((
            super(SearchView, self).get_cache_hash(request),
            self.search.get_query_string(),
        ))

    def get_context_data(self, **kwargs):
        object_list = self.search.page.results
        context = {
            'search': self.search,
            'object_list': object_list,
        }
        context_object_name = self.get_context_object_name(object_list)
        if context_object_name is not None:
            context[context_object_name] = object_list

        context.update(kwargs)
        return super(SearchView, self).get_context_data(**context)

    def get_context_object_name(self, object_list):
        if self.context_object_name:
            return self.context_object_name
        elif hasattr(object_list, 'model'):
            return '{0}_list'.format(object_list.model._meta.model_name)
        else:
            return None

    def get_default_ordering(self):
        return self.default_ordering

    def get_default_page_size(self):
        return self.default_page_size

    def get_filters(self):
        if self._filters is Undefined:
            filters = self.filters
            if not filters:
                return []
            if isinstance(filters, Iterable):
                filters = list(filters)
            else:
                filters = [filters]

            for filter in filters:
                if not isinstance(filter, type):
                    msg = '{cls}.filters should contain subclasses of Filter.'
                    raise ImproperlyConfigured(msg.format(cls=self.__class__.__name__))

            self._filters = filters

        return self._filters

    def get_orderings(self):
        if self._orderings is Undefined:
            orderings = self.orderings
            if not orderings:
                return []
            if isinstance(orderings, Iterable):
                orderings = list(orderings)
            else:
                orderings = [orderings]

            for i, ordering in enumerate(orderings):
                if not isinstance(ordering, type):
                    if not isinstance(ordering, tuple) or not ordering:
                        msg = ('{cls}.orderings should contain subclasses of'
                            ' Ordering or tuples with ordering data.')
                        raise ImproperlyConfigured(msg.format(cls=self.__class__.__name__))
                    elif len(ordering) == 1:
                        attrs = {
                            'name': ordering[0],
                            'fields': [ordering[0]],
                        }
                    elif len(ordering) == 2:
                        attrs = {
                            'name': ordering[0],
                            'fields': ordering[1],
                        }
                    else:
                        attrs = {
                            'name': ordering[0],
                            'fields': ordering[1],
                            'verbose_name': ordering[2],
                        }
                    orderings[i] = type(str('Ordering'), (Ordering, ), attrs)

            self._orderings = orderings

        return self._orderings

    def get_orphans(self):
        """
        Returns the maximum number of orphans extend the last page by when
        paginating.
        """
        return self.orphans

    def get_page_sizes(self):
        if self._page_sizes is Undefined:
            sizes = self.page_sizes
            if not sizes:
                return []
            elif isinstance(sizes, Iterable):
                sizes = list(sizes)
            else:
                sizes = [sizes]

            for i, size in enumerate(sizes):
                if not isinstance(size, type):
                    try:
                        size = int(size)
                    except (ValueError, TypeError):
                        msg = ('{cls}.page_sizes should contain subclasses of '
                            'PageSize or integer numbers.')
                        raise ImproperlyConfigured(msg.format(cls=self.__class__.__name__))
                    else:
                        sizes[i] = type(str('Size'), (PageSize, ), {'value': size})

            self._page_sizes = sizes

        return self._page_sizes

    def get_queryset(self):
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

    def get_search(self):
        return self.search_class(self)

    def get_selected_filters(self):
        filters = OrderedDict()
        raw_filters = self.request.GET.get(self.filters_kwarg)
        if raw_filters:
            for raw_filter in raw_filters.split(','):
                filter = raw_filter.split(':', 1)
                if len(filter) == 2:
                    name, value = filter
                    filters[name] = value.split(':')

        return filters

    def get_selected_ordering(self):
        return self.request.GET.get(self.ordering_kwarg)

    def get_selected_page(self):
        page = self.request.GET.get(self.page_kwarg)
        try:
            return int(page)
        except (ValueError, TypeError):
            return None

    def get_selected_page_size(self):
        size = self.request.GET.get(self.page_size_kwarg)
        try:
            return int(size)
        except (ValueError, TypeError):
            return None

    def get_template_names(self):
        """
        Return a list of template names to be used for the request. Must return
        a list. May not be called if render_to_response is overridden.
        """
        try:
            names = super(SearchView, self).get_template_names()
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

    def get_user_query(self):
        if not self.user_can_query:
            return None
        else:
            return self.request.GET.get(self.user_query_kwarg)

    def get_visible_pages(self):
        """
        Returns the maximum number of pages to render in the pagination block.
        """
        return self.visible_pages

