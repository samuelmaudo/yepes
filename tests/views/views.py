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

from .models import Article, Artist, Author, Book


class ArticleDetailView(DetailView):

    model = Article

    def get(self, request, *args, **kwargs):
        return HttpResponse(self.object.slug)


class DictList(ListView):
    """A ListView that doesn't use a model."""
    queryset = [
        {'first': 'John', 'last': 'Lennon'},
        {'first': 'Yoko', 'last': 'Ono'}
    ]
    template_name = 'views_tests/list.html'


class ArtistList(ListView):
    template_name = 'views_tests/list.html'
    queryset = Artist.objects.all()


class AuthorList(ListView):
    queryset = Author.objects.all()


class BookList(ListView):
    model = Book

