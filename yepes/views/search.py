# -*- coding:utf-8 -*-

from __future__ import division, unicode_literals

from collections import Iterable, OrderedDict

from django.core.exceptions import ImproperlyConfigured
from django.http import HttpResponse
from django.utils.encoding import force_text, python_2_unicode_compatible
from django.utils.html import escape
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _

from yepes.types import Undefined
from yepes.utils.http import urlquote_plus
from yepes.utils.properties import cached_property
from yepes.utils.structures import OrderedDictWhichIteratesOverValues
from yepes.views.list import (
    Ordering, Page, PageSize,
    AvailablePages, VisiblePages,
    ListQuery, ListView,
)


@python_2_unicode_compatible
class Facet(object):

    name = Undefined
    is_multiple = False
    verbose_name = Undefined

    def __init__(self, query):
        assert self.name is not Undefined
        self._query = query
        if self.verbose_name is Undefined:
            self.verbose_name = force_text(self.name).capitalize()

    def __eq__(self, other):
        return (isinstance(other, Facet) and self.name == other.name)

    def __hash__(self):
        return hash((self.__class__.__name__, self.name))

    def __ne__(self, other):
        return not self.__eq__(other)

    def __repr__(self):
        return str('<{0}: {1}>'.format(self.__class__.__name__, self.name))

    def __str__(self):
        return self.name

    def filter_objects(self, object_list, constraints=Undefined):
        raise NotImplementedError('Subclasses of Facet must override filter_objects() method')

    def get_constraints(self):
        raise NotImplementedError('Subclasses of Facet must override get_constraints() method')

    def get_selected_constraints(self):
        raise NotImplementedError('Subclasses of Facet must override get_selected_constraints() method')

    @cached_property
    def _constraints(self):
        return self._query._facets.get(self.name) or ()

    @cached_property
    def available_constraints(self):
        return OrderedDictWhichIteratesOverValues([
            (constraint.name, constraint)
            for constraint
            in self.get_constraints()
        ])

    @cached_property
    def constraints(self):
        constraints = OrderedDictWhichIteratesOverValues()
        for constraint in self.get_selected_constraints():
            constraints[constraint.name] = constraint
            if not self.is_multiple:
                break

        return constraints

    @cached_property
    def remove_url(self):
        facets = [
            f
            for f
            in self._query.facets
            if f != self
        ]
        return self._query.get_absolute_url(facets=facets, page=None)


@python_2_unicode_compatible
class Constraint(object):

    def __init__(self, facet, value, name=None, verbose_name=None, count=None):
        self._query = facet._query
        self.facet = facet
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
        return (isinstance(other, Constraint)
                and self.facet == other.facet
                and self.name == other.name)

    def __hash__(self):
        return hash((self.__class__.__name__, self.facet, self.name))

    def __ne__(self, other):
        return not self.__eq__(other)

    def __repr__(self):
        return str('<{0}: {1}>'.format(self.__class__.__name__, self.name))

    def __str__(self):
        return self.name

    def get_link(self):
        if self.count is None:
            if self.is_selected:
                template = '<a href="{remove_url}" class="selected" rel="nofollow">{verbose_name}</a>'
                kwargs = {
                    'remove_url': escape(self.remove_url),
                    'verbose_name': escape(self.verbose_name),
                }
            else:
                template = '<a href="{url}" rel="nofollow">{verbose_name}</a>'
                kwargs = {
                    'url': escape(self.url),
                    'verbose_name': escape(self.verbose_name),
                }
        else:
            if self.is_selected:
                template = '<a href="{remove_url}" class="selected" rel="nofollow">{verbose_name} <span class="count">({count})</span></a>'
                kwargs = {
                    'count': self.count,
                    'remove_url': escape(self.remove_url),
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
        return (self.name in self.facet.constraints)

    @cached_property
    def remove_url(self):
        facets = [
            f
            for f
            in self._query.facets
            if f != self.facet
        ]
        if self.facet.is_multiple:
            constraints = [
                constraint
                for constraint
                in self.facet.constraints
                if constraint != self
            ]
            if constraints:
                facets.append((self.facet, constraints))

        return self._query.get_absolute_url(facets=facets, page=None)

    @cached_property
    def url(self):
        facets = [
            f
            for f
            in self._query.facets
            if f != self.facet
        ]
        if self.facet.is_multiple:
            constraints = [
                constraint
                for constraint
                in self.facet.constraints
                if constraint != self
            ]
            constraints.append(self)
            facets.append((self.facet, constraints))
        else:
            facets.append((self.facet, [self]))

        return self._query.get_absolute_url(facets=facets, page=None)


class SearchQuery(ListQuery):

    def _filter_objects(self, object_list, user_query):
        user_query = self._prepare_user_query(user_query)
        if user_query:
            object_list = object_list.search(user_query)
        return object_list

    def _prepare_user_query(self, user_query):
        if user_query is Undefined:
            user_query = self.user_query
        return user_query

    def get_object_list(self, user_query=Undefined, ordering=Undefined,
                              page=Undefined, page_size=Undefined):
        object_list = self.space
        object_list = self._filter_objects(object_list, user_query)
        object_list = self._sort_objects(object_list, ordering)
        object_list = self._limit_objects(object_list, page, page_size)
        return object_list

    def get_query_string(self, user_query=Undefined, *args, **kwargs):
        params = []

        user_query = self._prepare_user_query(user_query)
        if user_query:
            params.append('{0}={1}'.format(
                self._user_query_kwarg,
                urlquote_plus(user_query, safe=''),
            ))

        extra = super(SearchQuery, self).get_query_string(*args, **kwargs)
        if extra:
            params.append(extra)

        return '&'.join(params)

    @cached_property
    def _user_query_kwarg(self):
        return self._view.user_query_kwarg

    @cached_property
    def available_orderings(self):
        orderings = OrderedDictWhichIteratesOverValues()
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
    def user_query(self):
        query = self._view.get_user_query()
        if query is None:
            return query
        else:
            return ' '.join(query.split())


class SearchView(ListView):

    query_class = SearchQuery
    search_signal = None
    user_query_kwarg = 'query'

    def dispatch(self, *args, **kwargs):
        response = super(SearchView, self).dispatch(*args, **kwargs)
        if (isinstance(response, HttpResponse)
                and response.status_code == 200
                and self.query.user_query):

            try:
                is_staff = self.request.user.is_staff
            except AttributeError:
                is_staff = False

            if not is_staff:
                self.send_search_signal(self.query.user_query, self.request)

        return response

    def get_template_names(self):
        names = super(SearchView, self).get_template_names()
        if not names or names[-1].endswith('_list.html'):
            model = self.get_model()
            if model is not None:
                names.insert(-1, '{0}/{1}_search.html'.format(
                    model._meta.app_label,
                    model._meta.model_name,
                ))
        return names

    def get_user_query(self):
        """
        Returns the query entered by the user.
        """
        return self.request.GET.get(self.user_query_kwarg)

    def send_search_signal(self, user_query, request):
        """
        Sends ``SearchView.search_signal`` if defined.
        """
        if self.search_signal is not None:
            self.search_signal.send(
                sender=self,
                query=user_query,
                request=request)


class FacetedSearchQuery(SearchQuery):

    def _filter_objects(self, object_list, user_query, facets):
        object_list = super(FacetedSearchQuery, self)._filter_objects(object_list, user_query)
        facets = self._prepare_facets(facets)
        if facets:
            for f in facets:
                if isinstance(f, Facet):
                    object_list = f.filter_objects(object_list, f.constraints)
                else:
                    facet, constraints = f
                    object_list = facet.filter_objects(object_list, constraints)
        return object_list

    def _prepare_facets(self, facets):
        if facets is Undefined:
            facets = self.facets
        return facets

    def get_object_list(self, user_query=Undefined, facets=Undefined,
                          ordering=Undefined, page=Undefined,
                          page_size=Undefined):
        object_list = self.space
        object_list = self._filter_objects(object_list, user_query, facets)
        object_list = self._sort_objects(object_list, ordering)
        object_list = self._limit_objects(object_list, page, page_size)
        return object_list

    def get_query_string(self, facets=Undefined, *args, **kwargs):
        params = []

        facets = self._prepare_facets(facets)
        if facets:
            facet_params = []
            for f in facets:
                if isinstance(f, Facet):
                    cons = f.constraints
                else:
                    f, cons = f

                facet_params.append('{0}:{1}'.format(f, ':'.join(
                    con.name
                    for con
                    in cons
                )))

            params.append('{0}={1}'.format(self._facets_kwarg, ','.join(facet_params)))

        extra = super(FacetedSearchQuery, self).get_query_string(*args, **kwargs)
        if extra:
            params.append(extra)

        return '&'.join(params)

    @cached_property
    def _facets(self):
        return self._view.get_selected_facets()

    @cached_property
    def _facets_kwarg(self):
        return self._view.facets_kwarg

    @cached_property
    def available_facets(self):
        facets = OrderedDictWhichIteratesOverValues()
        for facet_class in self._view.get_facets():
            facet = facet_class(self)
            facets[facet.name] = facet

        return facets

    @cached_property
    def facets(self):
        selected_facets = OrderedDictWhichIteratesOverValues()
        for name in self._facets:
            facet = self.available_facets.get(name)
            if facet is not None:
                selected_facets[facet.name] = facet

        return selected_facets


class FacetedSearchView(SearchView):

    facets = None
    _facets = Undefined
    facets_kwarg = 'filters'
    query_class = FacetedSearchQuery

    def get_facets(self):
        """
        Returns a list containing all available facets.
        """
        if self._facets is Undefined:
            self._facets = self.normalize_facets(self.facets)
        return self._facets

    def get_selected_facets(self):
        """
        Returns a list of facets which the user has selected.
        """
        facets = OrderedDict()
        raw_facets = self.request.GET.get(self.facets_kwarg)
        if raw_facets:
            for raw_facet in raw_facets.split(','):
                facet = raw_facet.split(':', 1)
                if len(facet) == 2:
                    name, value = facet
                    facets[name] = value.split(':')

        return facets

    def normalize_facets(self, facets):
        """
        Normalizes ``facets`` to a list of subclasses of ``Facet``.
        """
        if not facets:
            return []

        facets = list(facets)
        for facet in facets:
            if not isinstance(facet, type):
                msg = '{cls}.facets should contain subclasses of Facet.'
                raise ImproperlyConfigured(msg.format(cls=self.__class__.__name__))

        return facets

