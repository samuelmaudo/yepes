# -*- coding:utf-8 -*-

from yepes.utils.views import decorate_view
from yepes.view_mixins import (
    CacheMixin,
    CanonicalMixin,
    MessageMixin,
    ModelMixin,
)
from yepes.views.base import CachedTemplateView
from yepes.views.cache import CacheStatsView
from yepes.views.csrf import CsrfFailureView, csrf_failure_view
from yepes.views.detail import DetailView
from yepes.views.edit import FormView, CreateView, UpdateView, DeleteView
from yepes.views.list import ListView, ListAndCreateView
from yepes.views.search import SearchView
from yepes.views.static import StaticFileView
