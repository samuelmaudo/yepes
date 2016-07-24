# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from django.core.cache import (
    caches,
    DEFAULT_CACHE_ALIAS,
    InvalidCacheBackendError,
)
from django.core.management.base import BaseCommand, CommandError

from yepes.conf import settings


class Command(BaseCommand):
    help = ('Deletes all the keys in the specified caches. If no cache alias '
            'is passed, clears the default cache.')

    args = '<alias alias ...>'
    can_import_settings = True
    requires_system_checks = False

    def add_arguments(self, parser):
        parser.add_argument('args', metavar='cache_alias', nargs='*')
        parser.add_argument('-a', '--all',
            action='store_true',
            default=False,
            dest='all',
            help='Clears all the caches of your site.')

    def handle(self, *aliases, **options):
        if options['all']:
            aliases = list(settings.CACHES)
        elif not aliases:
            aliases = [DEFAULT_CACHE_ALIAS]

        selected_caches = []
        for alias in aliases:
            try:
                cache = caches[alias]
            except InvalidCacheBackendError:
                msg = "Cache '{0}' could not be found"
                raise CommandError(msg.format(alias))
            else:
                selected_caches.append((cache, alias))

        for cache, alias in selected_caches:
            self.stdout.write('Cleaning {0} ...'.format(alias))
            cache.clear()

        self.stdout.write('Caches were successfully cleaned.')

