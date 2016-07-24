# -*- coding:utf-8 -*-

from __future__ import unicode_literals

import hashlib
import re

from django import forms
from django.core.cache import cache
from django.core.exceptions import ObjectDoesNotExist
from django.utils import six
from django.utils.encoding import force_bytes, force_text

from yepes.contrib.registry.utils import get_site
from yepes.loading import LazyModel

__all__ = (
    'AlreadyRegisteredError', 'InvalidFieldError',
    'InvalidKeyError', 'UnregisteredError',
    'Registry', 'registry',
    'REGISTRY_KEYS',
)
Entry = LazyModel('registry', 'Entry')
LongEntry = LazyModel('registry', 'LongEntry')

KEY_RE = re.compile(r'^[a-zA-Z][a-zA-Z_-]*[a-zA-Z]$')
REGISTRY_KEYS = {}


class AlreadyRegisteredError(KeyError):

    def __init__(self, key):
        msg = "Key '{0!s}' is already registered."
        super(AlreadyRegisteredError, self).__init__(msg.format(key))
        self.key = key


class InvalidFieldError(ValueError):

    def __init__(self, field):
        msg = "'{0!r}' is not an instance of ``forms.Field``."
        super(InvalidFieldError, self).__init__(msg.format(field))
        self.field = field


class InvalidKeyError(KeyError):

    def __init__(self, key):
        msg = "'{0!s}' is not a well formed key."
        super(InvalidKeyError, self).__init__(msg.format(key))
        self.key = key


class UnregisteredError(KeyError):

    def __init__(self, key):
        msg = "There is no key '{0!s}'."
        super(UnregisteredError, self).__init__(msg.format(key))
        self.key = key


class Registry(object):

    namespace = None
    site_id = None
    _prefix = ''

    def __init__(self, site_id=None, namespace=None):
        if site_id:
            get_site(site_id)
            self.site_id = site_id
        if namespace:
            for token in namespace.split(':'):
                if not KEY_RE.search(token):
                    raise InvalidKeyError(namespace)
            else:
                self.namespace = namespace
                self._prefix = namespace + ':'

    def __contains__(self, key):
        return key in REGISTRY_KEYS

    def __delitem__(self, key):
        key = self.expand_key(key)
        model = self.get_model(self.get_field(key))
        model.all_objects.filter(site=self.site, key=key).delete()
        cache.delete(self.get_cache_key(key))

    def __getitem__(self, key):
        key = self.expand_key(key)
        field = self.get_field(key)
        cache_key = self.get_cache_key(key)
        value = cache.get(cache_key)
        if value is not None:
            return field.to_python(value)
        model = self.get_model(field)
        try:
            entry = model.all_objects.get(site=self.site, key=key)
        except ObjectDoesNotExist:
            value = field.initial
        else:
            value = field.to_python(entry.value)
        cache.set(cache_key, value)
        return value

    def __len__(self):
        return len(REGISTRY_KEYS)

    def __setitem__(self, key, value):
        key = self.expand_key(key)
        field = self.get_field(key)
        model = self.get_model(field)
        try:
            entry = model.all_objects.get(site=self.site, key=key)
        except ObjectDoesNotExist:
            entry = model(site=self.site, key=key)
        value = field.clean(value)
        try:
            entry.value = field.value_to_string(value)
        except AttributeError:
            entry.value = force_text(value)
        entry.save()
        cache.set(self.get_cache_key(key), value)

    def expand_key(self, key):
        if self._prefix and not key.startswith(self._prefix):
            return self._prefix + key
        else:
            return key

    def get(self, key, default=None):
        try:
            return self[key]
        except KeyError:
            return default

    def get_cache_key(self, key):
        hash = hashlib.md5(force_bytes(self.expand_key(key))).hexdigest()
        return 'yepes.registry.{0}.{1}'.format(self.site.pk, hash)

    def get_field(self, key):
        key = self.expand_key(key)
        if key not in REGISTRY_KEYS:
            raise UnregisteredError(key)
        else:
            return REGISTRY_KEYS[key]

    def get_model(self, field):
        if getattr(field, 'is_long', False):
            return LongEntry
        elif (hasattr(field, 'max_length')
                and (not field.max_length or field.max_length > 255)):
            return LongEntry
        else:
            return Entry

    def get_raw(self, key, default=None):
        try:
            key = self.expand_key(key)
            field = self.get_field(key)
            cache_key = 'raw:{0}'.format(self.get_cache_key(key))
            value = cache.get(cache_key)
            if value is not None:
                return value
            model = self.get_model(field)
            try:
                entry = model.all_objects.get(site=self.site, key=key)
            except ObjectDoesNotExist:
                value = field.initial
            else:
                value = entry.value
            cache.set(cache_key, value)
            return value
        except KeyError:
            return default

    def keys(self):
        return six.iterkeys(REGISTRY_KEYS)

    def register(self, key, field):
        for token in key.split(':'):
            if not KEY_RE.search(token):
                raise InvalidKeyError(key)
        key = self.expand_key(key)
        if key in REGISTRY_KEYS:
            raise AlreadyRegisteredError(key)
        if not isinstance(field, forms.Field):
            raise InvalidFieldError(field)
        REGISTRY_KEYS[key] = field

    @property
    def site(self):
        return get_site(self.site_id)


registry = Registry()

