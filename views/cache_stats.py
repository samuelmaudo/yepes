# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from django.contrib.admin.views.decorators import staff_member_required
from django.core.cache import cache
from django.core.cache.backends.memcached import BaseMemcachedCache
from django.core.urlresolvers import reverse_lazy
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.generic.base import TemplateView

from yepes.utils.views import decorate_view


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

