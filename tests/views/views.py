# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from django.http import HttpResponse

from yepes.views import (
    CachedTemplateView,
    CreateView,
    DeleteView,
    DetailView,
    FormView,
    ListView,
    ListAndCreateView,
    SearchView,
    StaticFileView,
    UpdateView,
)

from .models import Article


class ArticleDetailView(DetailView):

    model = Article

    def get(self, request, *args, **kwargs):
        return HttpResponse(self.object.slug)

