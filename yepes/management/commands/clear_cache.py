# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from optparse import make_option

from django.core.cache import (
    DEFAULT_CACHE_ALIAS,
    get_cache,
    InvalidCacheBackendError,
)
from django.core.management.base import BaseCommand, CommandError

from yepes.conf import settings


class Command(BaseCommand):
    help = ('Deletes all the keys in the specified caches. If no cache alias '
            'is passed, clears the default cache.')

    args = '<alias alias ...>'
    can_import_settings = True
    option_list = BaseCommand.option_list + (
        make_option('-a', '--all',
            action='store_true',
            default=False,
            dest='all',
            help='Clears all the caches of your site.'),
    )
    requires_model_validation = False

    def handle(self, *aliases, **options):

        if options['all']:
            aliases = list(settings.CACHES)
        elif not aliases:
            aliases = [DEFAULT_CACHE_ALIAS]

        caches = []
        for alias in aliases:
            try:
                cache = get_cache(alias)
            except InvalidCacheBackendError:
                msg = "Cache '{0}' could not be found"
                raise CommandError(msg.format(alias))
            else:
                caches.append((cache, alias))

        for cache, alias in caches:
            self.stdout.write('Cleaning {0} ...'.format(alias))
            cache.clear()

        self.stdout.write('Caches were successfully cleaned.')

