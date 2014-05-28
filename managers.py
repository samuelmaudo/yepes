# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from operator import ior, iand
import re
from string import punctuation

from django.db import connections
from django.db.models import get_models, Manager, Model, Q
from django.db.models.fields import CharField, TextField
from django.db.models.query import QuerySet
from django.utils import six, timezone
from django.utils.encoding import force_text
from django.utils.module_loading import import_by_path

from yepes.apps.registry import registry
from yepes.conf import settings

__all__ = (
    'ActivatableManager', 'ActivatableQuerySet',
    'DisplayableManager', 'DisplayableQuerySet',
    'EnableableManager', 'EnableableQuerySet',
    'PublishedManager', 'PublishedQuerySet',
    'SearchableManager', 'SearchableQuerySet',
    'SluggedManager',
)

try:
    from mptt.managers import TreeManager as NestableManager
except ImportError:
    pass
else:
    __all__ += ('NestableManager', )


def prepare_word(term):
    return force_text(term)


#def vowels_replace(matchobj):
    #vowel = matchobj.group(0)
    #if vowel.startswith('a'):
        #return '[aàáâä]'
    #if vowel.startswith('A'):
        #return '[AÀÁÀÄ]'
    #if vowel.startswith('e'):
        #return '[eèéêë]'
    #if vowel.startswith('E'):
        #return '[EÈÉÊË]'
    #if vowel.startswith('i'):
        #return '[iìíîï]'
    #if vowel.startswith('I'):
        #return '[IÌÍÎÏ]'
    #if vowel.startswith('o'):
        #return '[oòóôö]'
    #if vowel.startswith('O'):
        #return '[OÒÓÔÖ]'
    #if vowel.startswith('u'):
        #return '[uùúûü]'
    #if vowel.startswith('U'):
        #return '[UÙÚÛÜ]'
    #return vowel


#VOWELS_RE = re.compile(r'[aeiou][\u0300\u0301\u0302\u0308]?', re.I)


def vowels_replace(matchobj):
    vowel = matchobj.group(0)
    if vowel in 'aàáâä':
        return '[aàáâä]'
    elif vowel in 'AÀÁÀÄ':
        return '[AÀÁÀÄ]'
    elif vowel in 'eèéêë':
        return '[eèéêë]'
    elif vowel in 'EÈÉÊË':
        return '[EÈÉÊË]'
    elif vowel in 'iìíîï':
        return '[iìíîï]'
    elif vowel in 'IÌÍÎÏ':
        return '[IÌÍÎÏ]'
    elif vowel in 'oòóôö':
        return '[oòóôö]'
    elif vowel in 'OÒÓÔÖ':
        return '[OÒÓÔÖ]'
    elif vowel in 'uùúûü':
        return '[uùúûü]'
    elif vowel in 'UÙÚÛÜ':
        return '[UÙÚÛÜ]'
    return vowel


VOWELS_RE = re.compile(r'[aàáâäeèéêëiìíîïoòóôöuùúûü]', re.I)


class PublishedQuerySet(QuerySet):
    """
    QuerySet providing main search functionality for ``PublishedManager``.
    """

    def published(self, user=None, date=None):
        """
        Returns items with a published status and whose publication dates fall
        before and after the current date when specified.
        """
        from yepes.model_mixins import Displayable
        if user is not None and user.is_staff:
            return self.all()
        if not date:
            date = timezone.now()
        return self.filter(
            Q(publish_status=Displayable.PUBLISHED),
            Q(publish_from=None) | Q(publish_from__lte=date),
            Q(publish_to=None) | Q(publish_to__gte=date))

    def unpublished(self, user=None, date=None):
        """
        Returns items with published status but whose publication dates don't
        cover the current date.
        """
        from yepes.model_mixins import Displayable
        if not date:
            date = timezone.now()
        return self.filter(
            Q(publish_status=Displayable.PUBLISHED)
            | Q(publish_from__gt=date)
            | Q(publish_to__lt=date))


class PublishedManager(Manager):
    """
    Provides filter for restricting items returned by ``publish_status``,
    ``publish_from`` and `publish_to`.
    """

    def get_queryset(self):
        return PublishedQuerySet(self.model, using=self._db)

    def published(self, *args, **kwargs):
        """
        Returns items with published status and whose publication dates fall
        before and after the current date when specified.
        """
        return self.get_queryset().published(*args, **kwargs)

    def unpublished(self, *args, **kwargs):
        """
        Returns items with published status but whose publication dates don't
        cover the current date.
        """
        return self.get_queryset().unpublished(*args, **kwargs)


class SearchableQuerySet(QuerySet):
    """
    QuerySet providing main search functionality for ``SearchableManager``.
    """

    def __init__(self, *args, **kwargs):
        self._search_decorated = False
        self._search_fields = kwargs.pop('search_fields', {})
        self._search_ordered = False
        func = kwargs.pop('prepare_word', settings.SEARCH_PREPARE_WORD)
        self._search_prepare_word = import_by_path(func)
        self._search_terms = set()
        func = kwargs.pop('vowels_replace', settings.SEARCH_VOWELS_REPLACE)
        self._search_vowels_replace = import_by_path(func)
        super(SearchableQuerySet, self).__init__(*args, **kwargs)

    def __len__(self):
        """
        If search has occurred and no ordering has occurred, decorate each
        result with the number of search terms so that it can be sorted by the
        number of occurrence of terms.
        """
        if (self._result_cache is None
                and self._search_decorated
                and self._search_terms):

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
            super(SearchableQuerySet, self).__len__()
            results = self._result_cache

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

            for record in results:
                count = 0
                for field, weight in six.iteritems(self._search_fields):
                    for term in self._search_terms:
                        for value in get_values(record, field):
                            if isinstance(value, six.string_types) and value:
                                count += value.lower().count(term) * weight

                record.result_count = count

            if self._search_ordered:
                results.sort(key=lambda r: r.result_count, reverse=True)

            self.query.low_mark = low_mark
            self.query.high_mark = high_mark
            if high_mark:
                self._result_cache = results[low_mark:high_mark]
            elif low_mark:
                self._result_cache = results[low_mark:]
            else:
                self._result_cache = results

        return super(SearchableQuerySet, self).__len__()

    def _clone(self, *args, **kwargs):
        """
        Ensure attributes are copied to subsequent queries.
        """
        kwargs['_search_decorated'] = self._search_decorated
        kwargs['_search_fields'] = self._search_fields
        kwargs['_search_ordered'] = self._search_ordered
        kwargs['_search_terms'] = self._search_terms
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

    def search(self, query, search_fields=None, order_results=True,
                     decorate_results=True):
        """
        Build a queryset matching words in the given search query, treating
        quoted terms as exact phrases and taking into account + and - symbols
        as modifiers controlling which terms to require and exclude.
        """
        assert self.query.can_filter(), \
               'Cannot filter a query once a slice has been taken.'

        self._search_ordered = order_results
        self._search_decorated = order_results or decorate_results

        #### DETERMINE FIELDS TO SEARCH ###

        def search_fields_to_dict(fields):
            """
            Convert a sequence of fields to a weighted dict.
            """
            if not fields:
                return {}
            try:
                int(list(six.itervalues(dict(fields)))[0])
            except (TypeError, ValueError):
                return dict(zip(fields, [1] * len(fields)))
            else:
                return fields

        # Use fields arg if given, otherwise check internal list which if
        # empty, populate from model attr or char-like fields.
        if search_fields is None:
            search_fields = self._search_fields
        if len(search_fields) == 0:
            search_fields = {}
            for cls in reversed(self.model.__mro__):
                super_fields = getattr(cls, 'search_fields', {})
                search_fields.update(search_fields_to_dict(super_fields))
        if len(search_fields) == 0:
            search_fields = [
                f.name
                for f in self.model._meta.fields
                if issubclass(f.__class__, CharField)
                or issubclass(f.__class__, TextField)
            ]
        if len(search_fields) == 0:
            return self.none()

        # Search fields can be a dict or sequence of pairs mapping fields to
        # their relevant weight in ordering the results. If a mapping isn't
        # used then assume a sequence of field names and give them equal
        # weighting.
        if not isinstance(self._search_fields, dict):
            self._search_fields = {}
        self._search_fields.update(search_fields_to_dict(search_fields))

        #### BUILD LIST OF TERMS TO SEARCH FOR ###

        # Remove extra spaces, put modifiers inside quoted terms.
        terms = ' '.join(query.split()).replace('+"', '"+')    \
                                       .replace('-"', '"-')    \
                                       .split('"')

        # Strip punctuation other than modifiers from terms and create terms
        # list, first from quoted terms and then remaining words.
        terms = [
            (t[0] if t.startswith(('-', '+')) else '') + t.strip(punctuation)
            for t in terms[1::2] + ''.join(terms[::2]).split()
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
            return self.none()

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
            return self.none()
        else:
            self._search_terms.update(positive_terms)

        ### BUILD QUERYSET FILTER ###

        engine = connections[self.db].vendor
        if engine == 'mysql':
            template = r'[[:<:]]{0}[[:>:]]'
        elif engine == 'oracle':
            template = r'(^|\W){0}(\W|$)'
        elif engine == 'postgresql':
            template = r'\m{0}\M'
        elif engine == 'sqlite':
            template = r'\b{0}\b'
        else:
            template = r'(^|[^[:alnum:]_]){0}([^[:alnum:]_]|$)'

        def prep_field_lookup(field):
            return r'{0}__iregex'.format(field)

        def prep_term(term):
            term = self._search_prepare_word(term)
            term = VOWELS_RE.sub(self._search_vowels_replace, term)
            return template.format(term)

        # Create the queryset combining each set of terms.
        field_lookups = [
            prep_field_lookup(f)
            for f
            in six.iterkeys(search_fields)
        ]
        excluded = []
        required = []
        optional = []
        for t in terms:
            if t.startswith('-'):
                term = prep_term(t[1:])
                excluded.append(reduce(
                    iand,
                    [~Q(**{lookup: term}) for lookup in field_lookups]
                ))
            elif t.startswith('+'):
                term = prep_term(t[1:])
                required.append(reduce(
                    ior,
                    [Q(**{lookup: term}) for lookup in field_lookups]
                ))
            else:
                term = prep_term(t)
                optional.append(reduce(
                    ior,
                    [Q(**{lookup: term}) for lookup in field_lookups]
                ))
        queryset = self._clone()
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
        self._search_ordered = False
        return super(SearchableQuerySet, self).order_by(*field_names)


class SearchableManager(Manager):
    """
    Manager providing a chainable queryset.

    Adapted from Mezzanine built-in search engine. Supports Mezzanine API but
    provides more accurate results and is capable to search across related
    fields.

    """
    def __init__(self, *args, **kwargs):
        self._search_fields = kwargs.pop('search_fields', [])
        super(SearchableManager, self).__init__(*args, **kwargs)

    def get_queryset(self):
        kwargs = {
            'search_fields': self._search_fields,
            'using': self._db,
        }
        return SearchableQuerySet(self.model, **kwargs)

    def search(self, *args, **kwargs):
        """
        Proxy to queryset's search method for the manager's model and any
        models that subclass from this manager's model if the model is
        abstract.
        """
        if getattr(self.model._meta, 'abstract', False):
            models = [m for m in get_models() if issubclass(m, self.model)]
            # Strip out any models that are superclasses of models.
            parents = reduce(ior, [m._meta.get_parent_list() for m in models])
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

        return sorted(results, key=lambda r: r.result_count, reverse=True)


class SluggedManager(Manager):
    """
    Provides access to items using their natural key: the ``slug`` field.
    """
    def get_by_natural_key(self, slug):
        return self.get(slug=slug)


class ActivatableQuerySet(QuerySet):
    """
    QuerySet providing main search functionality for ``ActivatableManager``.
    """

    def active(self, user=None, date=None):
        """
        Returns active items whose activation dates fall before and after the
        current date when specified.
        """
        if user is not None and user.is_staff:
            return self.all()
        if not date:
            date = timezone.now()
        return self.filter(
            Q(active_status=True),
            Q(active_from=None) | Q(active_from__lte=date),
            Q(active_to=None) | Q(active_to__gte=date))

    def inactive(self, user=None, date=None):
        """
        Returns inactive items or active items whose activation dates don't
        cover the current date.
        """
        if not date:
            date = timezone.now()
        return self.filter(
            Q(active_status=False)
            | Q(active_from__gt=date)
            | Q(active_to__lt=date))


class ActivatableManager(Manager):
    """
    Provides filter for restricting items returned by ``active_status``,
    ``active_from`` and ``active_to``.
    """

    def get_queryset(self):
        return ActivatableQuerySet(self.model, using=self._db)

    def active(self, *args, **kwargs):
        """
        Returns active items whose activation dates fall before and after the
        current date when specified.
        """
        return self.get_queryset().active(*args, **kwargs)

    def inactive(self, *args, **kwargs):
        """
        Returns inactive items or active items whose activation dates don't
        cover the current date.
        """
        return self.get_queryset().inactive(*args, **kwargs)


class DisplayableQuerySet(PublishedQuerySet, SearchableQuerySet):
    """
    QuerySet providing main search functionality for ``PublishedManager``.
    """
    pass


class DisplayableManager(PublishedManager, SearchableManager, SluggedManager):
    """
    Manually combines ``PublishedManager``, ``SearchableManager`` and
    ``SluggedManager`` for the ``Displayable`` model.
    """
    def get_queryset(self):
        kwargs = {
            'search_fields': self._search_fields,
            'using': self._db,
        }
        return DisplayableQuerySet(self.model, **kwargs)


class EnableableQuerySet(QuerySet):
    """
    QuerySet providing main search functionality for ``EnableableManager``.
    """

    def disabled(self, user=None):
        """
        Returns disabled items.
        """
        return self.filter(is_enabled=False)

    def enabled(self, user=None):
        """
        Returns enabled items.
        """
        if user is not None and user.is_staff:
            return self.all()
        return self.filter(is_enabled=True)


class EnableableManager(Manager):
    """
    Provides filter for restricting items returned by ``is_enabled``.
    """

    def get_queryset(self):
        return EnableableQuerySet(self.model, using=self._db)

    def disabled(self, *args, **kwargs):
        """
        Returns disabled items.
        """
        return self.get_queryset().disabled(*args, **kwargs)

    def enabled(self, *args, **kwargs):
        """
        Returns enabled items.
        """
        return self.get_queryset().enabled(*args, **kwargs)

