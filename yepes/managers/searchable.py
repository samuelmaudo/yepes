# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from operator import ior, iand
import re
from string import punctuation

from django.db import connections
from django.db.models import Manager, Model, Q
from django.db.models.fields import CharField, TextField
from django.db.models.manager import ManagerDescriptor
from django.db.models.query import QuerySet
from django.utils import six
from django.utils.encoding import force_text
from django.utils.module_loading import import_string
from django.utils.six.moves import reduce, zip

from yepes.apps import apps
from yepes.conf import settings
from yepes.contrib.registry import registry
from yepes.types import Undefined


def search_fields_to_dict(fields):
    """
    In ``SearchableQuerySet`` and ``SearchableManager``, search fields
    can either be a sequence, or a dict of fields mapped to weights.
    This function converts sequences to a dict mapped to even weights,
    so that we're consistently dealing with a dict of fields mapped to
    weights, eg:

        ("title", "content") -> {"title": 1, "content": 1}

    """
    if not fields:
        return {}
    try:
        int(list(six.itervalues(dict(fields)))[0])
    except (TypeError, ValueError):
        return dict(zip(fields, [1] * len(fields)))
    else:
        return fields


class SearchableHelper(object):

    #vowels_re = re.compile(r'[aeiouAEIOU][\u0300\u0301\u0302\u0308]?')
    vowels_re = re.compile(r'[aàáâäAÀÁÀÄeèéêëEÈÉÊËiìíîïIÌÍÎÏoòóôöOÒÓÔÖuùúûüUÙÚÛÜ]')

    @staticmethod
    def clean_term(term):
        return force_text(term)

    @staticmethod
    def prepare_field_lookup(field):
        return r'{0}__iregex'.format(field)

    @classmethod
    def prepare_term(cls, term, engine):
        term = cls.clean_term(term)
        term = cls.vowels_re.sub(cls.vowels_replace, term)
        if engine == 'postgresql':
            template = r'\m{0}\M'
        elif engine == 'mysql':
            template = r'[[:<:]]{0}[[:>:]]'
        elif engine == 'oracle':
            template = r'(^|\W){0}(\W|$)'
        elif engine == 'sqlite':
            template = r'\b{0}\b'
        else:
            template = r'(^|[^[:alnum:]_]){0}([^[:alnum:]_]|$)'

        return template.format(term)

    #@staticmethod
    #def vowels_replace(matchobj):
        #vowel = matchobj.group(0)
        #if vowel.startswith(('a', 'A')):
            #return '[aàáâäAÀÁÀÄ]'
        #if vowel.startswith(('e', 'E')):
            #return '[eèéêëEÈÉÊË]'
        #if vowel.startswith(('i', 'I')):
            #return '[iìíîïIÌÍÎÏ]'
        #if vowel.startswith(('o', 'O')):
            #return '[oòóôöOÒÓÔÖ]'
        #if vowel.startswith(('u', 'U')):
            #return '[uùúûüUÙÚÛÜ]'
        #return vowel

    @staticmethod
    def vowels_replace(matchobj):
        vowel = matchobj.group(0)
        if vowel in 'aàáâäAÀÁÀÄ':
            return '[aàáâäAÀÁÀÄ]'
        elif vowel in 'eèéêëEÈÉÊË':
            return '[eèéêëEÈÉÊË]'
        elif vowel in 'iìíîïIÌÍÎÏ':
            return '[iìíîïIÌÍÎÏ]'
        elif vowel in 'oòóôöOÒÓÔÖ':
            return '[oòóôöOÒÓÔÖ]'
        elif vowel in 'uùúûüUÙÚÛÜ':
            return '[uùúûüUÙÚÛÜ]'
        return vowel


class SearchableQuerySet(QuerySet):
    """
    QuerySet providing main search functionality for ``SearchableManager``.
    """

    def __init__(self, *args, **kwargs):
        self._search_decorated = False
        self._search_fields = kwargs.pop('search_fields', {})
        self._search_helper = kwargs.pop('search_helper', settings.SEARCH_HELPER)
        self._search_ordered = False
        self._search_terms = set()
        super(SearchableQuerySet, self).__init__(*args, **kwargs)

    def _clone(self, *args, **kwargs):
        """
        Ensure attributes are copied to subsequent queries.
        """
        kwargs['_search_decorated'] = self._search_decorated
        kwargs['_search_fields'] = self._search_fields.copy()
        kwargs['_search_helper'] = self._search_helper
        kwargs['_search_ordered'] = self._search_ordered
        kwargs['_search_terms'] = self._search_terms.copy()
        return super(SearchableQuerySet, self)._clone(*args, **kwargs)

    def count(self):
        """
        Mark the filter as being ordered if search has occurred.
        """
        count = super(SearchableQuerySet, self).count()
        if self._search_decorated and count > settings.SEARCH_RESULT_LIMIT:
            return settings.SEARCH_RESULT_LIMIT
        else:
            return count

    def iterator(self):
        """
        If search has occurred and no ordering has occurred, decorate each
        result with the number of search terms so that it can be sorted by the
        number of occurrence of terms.
        """
        if not self._search_decorated and not self._search_terms:
            return super(SearchableQuerySet, self).iterator()

        self._prefetch_related_lookups.extend([
            f[:f.rindex('__')]
            for f
            in self._search_fields
            if '__' in f
        ])
        low_mark = self.query.low_mark
        high_mark = self.query.high_mark
        self.query.low_mark = 0
        self.query.high_mark = None
        results = list(super(SearchableQuerySet, self).iterator())

        def get_values(obj, fields):
            fields = fields.split('__')
            values = [getattr(obj, fields[0])]

            for f in fields[1:]:
                objects = values
                values = []
                for obj in objects:
                    if isinstance(obj, Model):
                        values.append(getattr(obj, f))
                    else:
                        # It is a manager.
                        for o in obj.all():
                            values.append(getattr(o, f))

            return values

        for instance in results:
            score = 0
            for field, weight in six.iteritems(self._search_fields):
                for term in self._search_terms:
                    for value in get_values(instance, field):
                        if isinstance(value, six.string_types) and value:
                            score += value.lower().count(term) * weight

            instance.search_score = score

        if self._search_ordered:
            results.sort(key=lambda r: r.search_score, reverse=True)

        self.query.low_mark = low_mark
        self.query.high_mark = high_mark
        if high_mark:
            results = results[low_mark:high_mark]
        elif low_mark:
            results = results[low_mark:]

        return iter(results)

    def search(self, query, search_fields=None, order_results=True,
                     decorate_results=True):
        """
        Build a queryset matching words in the given search query, treating
        quoted terms as exact phrases and taking into account + and - symbols
        as modifiers controlling which terms to require and exclude.
        """
        assert self.query.can_filter(), \
               'Cannot filter a query once a slice has been taken.'

        helper = import_string(self._search_helper)
        queryset = self._clone()
        queryset._search_ordered = order_results
        queryset._search_decorated = order_results or decorate_results

        #### DETERMINE FIELDS TO SEARCH ###

        # Use search_fields argument if given, otherwise use queryset._search_fields
        # property (which is initially configured by the manager class).
        if search_fields:
            queryset._search_fields = search_fields_to_dict(search_fields)
        if not queryset._search_fields:
            return queryset.none()

        #### BUILD LIST OF TERMS TO SEARCH FOR ###

        # Remove extra spaces, put modifiers inside quoted terms.
        terms = ' '.join(query.split()).replace('+"', '"+')    \
                                       .replace('-"', '"-')    \
                                       .split('"')

        # Strip punctuation other than modifiers from terms and create terms
        # list, first from quoted terms and then remaining words.
        terms = [
            (t[0] if t.startswith(('-', '+')) else '') + t.strip(punctuation)
            for t
            in terms[1::2] + ''.join(terms[::2]).split()
        ]

        # Remove stop words from terms that aren't quoted or use modifiers,
        # since words with these are an explicit part of the search query.
        # If doing so ends up with an empty term list, then keep the stop
        # words.
        terms_no_stopwords = [
            t
            for t in terms
            if t.startswith(('-', '+', '"'))
            or t.lower() not in registry['core:STOP_WORDS']
        ]
        positive_terms = [
            (t if not t.startswith('+') else t[1:]).lower()
            for t in terms_no_stopwords
            if not t.startswith('-')
        ]
        if not positive_terms:
            positive_terms = [
                (t if not t.startswith('+') else t[1:]).lower()
                for t in terms
                if not t.startswith('-')
            ]
        else:
            terms = terms_no_stopwords

        # Avoid too short or too long queries.
        query_len = len(''.join(terms))
        if (query_len < settings.SEARCH_MIN_QUERY_LEN
                or query_len > settings.SEARCH_MAX_QUERY_LEN):
            return queryset.none()

        # Remove too short words.
        positive_terms = [
            t
            for t in positive_terms
            if len(t) >= settings.SEARCH_MIN_WORD_LEN
        ]
        terms = [
            t
            for t in terms
            if len(t.strip('-+')) >= settings.SEARCH_MIN_WORD_LEN
        ]

        # Append positive terms (those without the negative modifier) to the
        # internal list for sorting when results are iterated.
        if not positive_terms:
            return queryset.none()
        else:
            queryset._search_terms.update(positive_terms)

        ### BUILD QUERYSET FILTER ###

        engine = connections[queryset.db].vendor

        # Filter the queryset combining each set of terms.
        field_lookups = [
            helper.prepare_field_lookup(f)
            for f
            in six.iterkeys(queryset._search_fields)
        ]
        excluded = []
        required = []
        optional = []
        for t in terms:
            if t.startswith('-'):
                term = helper.prepare_term(t[1:], engine)
                excluded.append(reduce(
                    iand,
                    [~Q(**{lookup: term}) for lookup in field_lookups]
                ))
            elif t.startswith('+'):
                term = helper.prepare_term(t[1:], engine)
                required.append(reduce(
                    ior,
                    [Q(**{lookup: term}) for lookup in field_lookups]
                ))
            else:
                term = helper.prepare_term(t, engine)
                optional.append(reduce(
                    ior,
                    [Q(**{lookup: term}) for lookup in field_lookups]
                ))

        queryset.query.add_distinct_fields()
        queryset.query.clear_ordering(force_empty=True)
        if excluded:
            queryset = queryset.filter(reduce(iand, excluded))
        if required:
            queryset = queryset.filter(reduce(iand, required))
        elif optional:
            # Optional terms aren't relevant to the filter if there are terms
            # that are explicitly required.
            queryset = queryset.filter(reduce(ior, optional))

        return queryset

    def order_by(self, *field_names):
        """
        Mark the filter as being ordered if search has occurred.
        """
        if field_names == ('search_score', ):
            queryset = super(SearchableQuerySet, self).order_by()
            queryset._search_ordered = True
            queryset._search_decorated = True
        else:
            queryset = super(SearchableQuerySet, self).order_by(*field_names)
            queryset._search_ordered = False

        return queryset


class SearchableManager(Manager):
    """
    Manager providing a chainable queryset.

    Adapted from Mezzanine built-in search engine. Supports Mezzanine API but
    provides more accurate results and is capable to search across related
    fields.

    """
    def __init__(self, *args, **kwargs):
        self._search_fields = kwargs.pop('search_fields', {})
        self._cleaned_search_fields = Undefined
        super(SearchableManager, self).__init__(*args, **kwargs)

    def contribute_to_class(self, model, name):
        """
        Django 1.5 explicitly prevents managers being accessed from
        abstract classes, which is behaviour the search API has relied
        on for years. Here we reinstate it.
        """
        super(SearchableManager, self).contribute_to_class(model, name)
        setattr(model, name, ManagerDescriptor(self))

    def get_queryset(self):
        kwargs = {
            'search_fields': self.get_search_fields(),
            'using': self._db,
        }
        return SearchableQuerySet(self.model, **kwargs)

    def get_search_fields(self):
        """
        Returns the search field names mapped to weights as a dict.
        Used in ``get_query_set`` below to tell ``SearchableQuerySet``
        which search fields to use. Also used by ``DisplayableAdmin``
        to populate Django admin's ``search_fields`` attribute.

        Search fields can be populated via
        ``SearchableManager.__init__``, which then get stored in
        ``SearchableManager._search_fields``, which serves as an
        approach for defining an explicit set of fields to be used.

        Alternatively and more commonly, ``search_fields`` can be
        defined on models themselves. In this case, we look at the
        model and all its base classes, and build up the search
        fields from all of those, so the search fields are implicitly
        built up from the inheritence chain.

        Finally if no search fields have been defined at all, we
        fall back to any fields that are ``CharField`` or ``TextField``
        instances.

        """
        if self._cleaned_search_fields is Undefined:

            search_fields = self._search_fields.copy()

            if not search_fields:
                for cls in reversed(self.model.__mro__):
                    super_fields = getattr(cls, 'search_fields', {})
                    search_fields.update(search_fields_to_dict(super_fields))

            if not search_fields:
                search_fields = {
                    f.name: 1
                    for f in self.model._meta.fields
                    if isinstance(f, (CharField, TextField))
                }

            self._cleaned_search_fields = search_fields

        return self._cleaned_search_fields.copy()

    def search(self, *args, **kwargs):
        """
        Proxy to queryset's search method for the manager's model and any
        models that subclass from this manager's model if the model is
        abstract.
        """
        if getattr(self.model._meta, 'abstract', False):
            models = [
                m
                for m
                in apps.get_models()
                if issubclass(m, self.model)
            ]
            parents = reduce(ior, [
                set(m._meta.get_parent_list())
                for m in
                models
            ])
            # Strip out any models that are superclasses of models.
            models = [m for m in models if m not in parents]
        else:
            models = [self.model]

        kwargs['order_results'] = False
        kwargs['decorate_results'] = True
        user = kwargs.pop('user', None)
        customer = kwargs.pop('customer', None)
        results = []
        for model in models:
            qs = model._default_manager.get_queryset()
            if hasattr(qs, 'active'):
                qs = qs.active(user)
            if hasattr(qs, 'available'):
                qs = qs.available(user, customer)
            if hasattr(qs, 'enabled'):
                qs = qs.enabled(user)
            if hasattr(qs, 'published'):
                qs = qs.published(user)
            results.extend(qs.search(*args, **kwargs))

        return sorted(results, key=lambda r: r.search_score, reverse=True)

