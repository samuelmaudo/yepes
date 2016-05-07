# -*- coding:utf-8 -*-

from __future__ import unicode_literals, with_statement

from collections import OrderedDict
from copy import copy
from time import time
from weakref import ref as weakref

from django.core.cache import caches
from django.core.exceptions import ImproperlyConfigured, ObjectDoesNotExist
from django.db.models.manager import (
    Manager,
    ManagerDescriptor,
    AbstractManagerDescriptor,
    SwappedManagerDescriptor,
)
from django.db.models.signals import post_save, post_delete
from django.utils import six
from django.utils.synch import RWLock

from yepes.conf import settings
from yepes.contrib.registry import registry
from yepes.types import Undefined
from yepes.utils.properties import cached_property

__all__ = ('MintCache', 'LookupTable')

# Global in-memory store of cache data. Keyed by name, to provide multiple
# named local memory caches.
CACHES = {}
CACHE_INFO = {}
LOCKS = {}


class MintCache(object):
    """
    MintCache instances wrap standard cache backends but slightly modify their
    behavior:

    Each entry is stored packed with the desired cache expire time and, each
    time the entry is retrieved from cache, the packed expiry time is checked.
    If it has passed, the stale cache entry is stored again with a new expiry
    time that has a ``delay`` added to it. In this case the entry is not
    returned, so that a cache miss occurs and the entry should be set by the
    caller, but all other callers will still get the stale entry.

    This approach ensures that cache misses never actually occur and that
    (almost) only one client will perform regeneration of a cache entry.

    Based on an snippet (https://djangosnippets.org/snippets/793/) created
    by Disqus.

    """
    def __init__(self, cache, timeout=None, delay=None):
        if isinstance(cache, six.string_types):
            cache = caches[cache]
        self._cache = cache
        self._timeout = timeout or settings.MINT_CACHE_SECONDS
        self._delay = delay or settings.MINT_CACHE_DELAY_SECONDS

    def __contains__(self, key):
        return self.has_key(key)

    def add(self, key, value, timeout=None):
        """
        Stores a packed value in the cache if the key does not already exist.

        Returns True if the value was stored, False otherwise.

        """
        if timeout is None:
            timeout = self._timeout

        refresh_time = timeout + time()
        real_timeout = timeout + self._delay
        packed_value = (value, refresh_time, False)
        return self._cache.add(key, packed_value, real_timeout)

    def clear(self):
        """
        Removes *all* values from the cache at once.
        """
        self._cache.clear()

    def close(self, **kwargs):
        """
        Closes the cache connection.
        """
        self._cache.close(**kwargs)

    def delete(self, key):
        """
        Deletes a key from the cache, failing silently.
        """
        self._cache.delete(key)

    def get(self, key, default=None):
        """
        Retrieves the cache entry and checks its expiry time. If has past,
        puts the stale entry back into cache, and does not return it. This
        forces to refresh entry value.
        """
        packed_value = self._cache.get(key)
        if packed_value is None:
            return default

        value, refresh_time, refreshed = packed_value
        if time() > refresh_time and not refreshed:
            self.set(key, value, self._delay, True)
        else:
            return value

    def has_key(self, key):
        """
        Returns True if the key is in the cache and has not expired.
        """
        self._cache.has_key(key)

    def set(self, key, value, timeout=None, refreshed=False):
        """
        Stores the cache entry packed with the desired cache expiry time.
        """
        if timeout is None:
            timeout = self._timeout

        refresh_time = timeout + time()
        real_timeout = timeout + self._delay
        packed_value = (value, refresh_time, refreshed)
        self._cache.set(key, packed_value, real_timeout)


class LookupTable(object):

    default_registry_key = None
    indexed_fields = None
    name = None
    prefetch_related = None
    timeout = 600
    use_in_migrations = False

    def __init__(self, indexed_fields=None, prefetch_related=None, timeout=None,
                       default_registry_key=None):
        self._set_creation_counter()
        self._inherited = False

        if not indexed_fields:
            indexed_fields = self.indexed_fields

        self.indexed_fields = set()
        if indexed_fields:
            self.indexed_fields.update(indexed_fields)
            self.indexed_fields.discard('pk')

        if prefetch_related is not None:
            self.prefetch_related = prefetch_related

        if timeout is not None:
            self.timeout = timeout

        if default_registry_key is not None:
            self.default_registry_key = default_registry_key

    def __get__(self, obj, cls=None):
        if obj is not None:
            msg = "``LookupTable`` isn't accessible via {0} instances."
            raise AttributeError(msg.format(cls.__name__))
        else:
            return self

    def _copy_to_model(self, model):
        assert issubclass(model, self.model)
        mgr = copy(self)
        mgr._set_creation_counter()
        mgr._set_model(model)
        mgr._inherited = True
        return mgr

    def _is_populated(self):
        return (time() < self._info['expire_time'])

    def _maybe_populate(self):
        if not self._is_populated():
            self.populate()

    def _model_changed(self, sender, instance, **kwargs):
        if getattr(instance, '_clear_lookup_table', True):
            self.clear()

    def _parse_args(self, args, kwargs):
        if args:
            if len(args) != 1 or len(kwargs) != 0:
                raise AttributeError
            cache = self._cache
            field = 'pk'
            key = args[0]
        elif kwargs:
            if len(args) != 0 or len(kwargs) != 1:
                raise AttributeError
            field, key = kwargs.popitem()
            if field in ('pk', self.model_pk):
                cache = self._cache
            elif field in self.indexed_fields:
                cache = self._indexes[field]
            else:
                raise KeyError
        else:
            raise AttributeError

        return cache, field, key

    def _set_creation_counter(self):
        self.creation_counter = Manager.creation_counter
        Manager.creation_counter += 1

    def _set_model(self, model):
        cache_name = '{0}.{1}.{2}'.format(
            model._meta.app_label,
            model._meta.model_name,
            self.name,
        )
        self._cache = CACHES.setdefault(cache_name, OrderedDict())
        self._info = CACHE_INFO.setdefault(cache_name, {'expire_time': 0})
        self._lock = LOCKS.setdefault(cache_name, RWLock())

        self._indexes = {}
        for field_name in self.indexed_fields:
            cache_name = '{0}.{1}.{2}.{3}'.format(
                model._meta.app_label,
                model._meta.model_name,
                self.name,
                field_name,
            )
            self._indexes[field_name] = CACHES.setdefault(cache_name, {})

        self._model_ref = weakref(model)

    def all(self):
        self._maybe_populate()
        with self._lock.reader():
            return list(six.itervalues(self._cache))

    def clear(self):
        with self._lock.writer():
            self._cache.clear()
            self._info['expire_time'] = 0
            for index in six.itervalues(self._indexes):
                index.clear()

    def contribute_to_class(self, model, name):
        self._set_model(model)
        if not self.name:
            self.name = name

        # Only contribute the manager if the model is concrete.
        opts = model._meta
        if opts.abstract:
            setattr(model, name, AbstractManagerDescriptor(model))
        elif opts.swapped:
            setattr(model, name, SwappedManagerDescriptor(model))
        else:
            post_save.connect(self._model_changed, sender=model)
            post_delete.connect(self._model_changed, sender=model)
            setattr(model, name, ManagerDescriptor(self))

        abstract = (opts.abstract or (self._inherited and not opts.proxy))
        opts.managers.append((self.creation_counter, self, abstract))

    def create(self, **kwargs):
        record = self.model(**kwargs)
        record._clear_lookup_table = False
        #post_save.disconnect(self._model_changed, sender=self.model)
        record.save(force_insert=True)
        #post_save.connect(self._model_changed, sender=self.model)
        del record._clear_lookup_table
        if self._is_populated():
            with self._lock.writer():
                self._cache[getattr(record, self.model_pk)] = record
                for field, index in six.iteritems(self._indexes):
                    index[getattr(record, field)] = record

        return record

    def exists(self, *args, **kwargs):
        cache, field, key = self._parse_args(args, kwargs)
        self._maybe_populate()
        with self._lock.reader():
            return (key in cache)

    def exists_many(self, *args, **kwargs):
        cache, field, keys = self._parse_args(args, kwargs)
        self._maybe_populate()
        with self._lock.reader():
            return all(k in cache for k in keys)

    def fetch_records(self):
        qs = self.model._default_manager.get_queryset()
        if self.prefetch_related:
            qs = qs.prefetch_related(*self.prefetch_related)
        return qs

    def get(self, *args, **kwargs):
        default = kwargs.pop('default', None)
        cache, field, key = self._parse_args(args, kwargs)
        self._maybe_populate()
        with self._lock.reader():
            return cache.get(key, default)

    def get_default(self):
        if self.default_registry_key is None:
            msg = ('{cls}.default_registry_key is undefined.'
                   ' Define {cls}.default_registry_key'
                   ' or override {cls}.get_default().')
            raise ImproperlyConfigured(msg.format(cls=self.__class__.__name__))

        record = None
        record_id = registry.get_raw(self.default_registry_key)
        if record_id is not None:
            record = self.get(int(record_id))
            if record is None:
                try:
                    record = registry.get(self.default_registry_key)
                except ObjectDoesNotExist:
                    pass

        return record

    def get_many(self, *args, **kwargs):
        default = kwargs.pop('default', None)
        cache, field, keys = self._parse_args(args, kwargs)
        self._maybe_populate()
        with self._lock.reader():
            return [cache.get(k, default) for k in keys]

    def get_or_create(self, *args, **kwargs):
        if 'default' in kwargs:
            raise AttributeError

        defaults = kwargs.pop('defaults', {})
        record = self.get(*args, **kwargs)
        if record is None:
            cache, field, key = self._parse_args(args, kwargs)
            defaults[field] = key
            record = self.create(**defaults)
            created = True
        else:
            created = False

        return (record, created)

    def has_default(self):
        return (self.default_registry_key is not None)

    def populate(self):
        self.clear()
        with self._lock.writer():
            for record in self.fetch_records():
                record._clear_lookup_table = False
                self._cache[getattr(record, self.model_pk)] = record
                for field, index in six.iteritems(self._indexes):
                    index[getattr(record, field)] = record

            self._info['expire_time'] = time() + self.timeout

    @property
    def model(self):
        return self._model_ref()

    @cached_property
    def model_pk(self):
        return self.model._meta.pk.name

