# -*- coding:utf-8 -*-

from yepes.utils.views import decorate_view
from yepes.view_mixins import (
    CacheMixin,
    CanonicalMixin,
    MessageMixin,
    ModelMixin,
)
from yepes.views.base import CachedTemplateView
from yepes.views.cache_stats import CacheStatsView
from yepes.views.csrf_failure import CsrfFailureView, csrf_failure_view
from yepes.views.detail import DetailView
from yepes.views.edit import FormView, CreateView, UpdateView, DeleteView
from yepes.views.list import ListView, ListAndCreateView
