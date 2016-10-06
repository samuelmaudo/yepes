# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from django.conf.urls import url

from . import views

urlpatterns = [

    # DetailView
    url(r'^detail/(?P<slug>[-\w]+)/$',
        views.ArticleDetailView.as_view(),
        name='article_detail'),

    # ListView
    url(r'^list/dict/$',
        views.DictList.as_view()),
    url(r'^list/dict/paginated/$',
        views.DictList.as_view(page_size=1)),
    url(r'^list/artists/$',
        views.ArtistList.as_view(),
        name="artists_list"),
    url(r'^list/authors/$',
        views.AuthorList.as_view(),
        name="authors_list"),
    url(r'^list/authors/paginated/$',
        views.AuthorList.as_view(page_size=30)),
    url(r'^list/authors/paginated-orphaned/$',
        views.AuthorList.as_view(page_size=30, orphans=2)),
    url(r'^list/authors/notempty/$',
        views.AuthorList.as_view(allow_empty=False)),
    url(r'^list/authors/notempty/paginated/$',
        views.AuthorList.as_view(allow_empty=False, page_size=2)),
    url(r'^list/authors/template_name/$',
        views.AuthorList.as_view(template_name='views_tests/list.html')),
    url(r'^list/authors/template_name_suffix/$',
        views.AuthorList.as_view(template_name_suffix='_objects')),
    url(r'^list/authors/context_object_name/$',
        views.AuthorList.as_view(context_object_name='author_list')),
    url(r'^list/authors/dupe_context_object_name/$',
        views.AuthorList.as_view(context_object_name='object_list')),
    url(r'^list/authors/invalid/$',
        views.AuthorList.as_view(queryset=None)),
    url(r'^list/authors/paginated/custom_page_kwarg/$',
        views.AuthorList.as_view(page_size=30, page_kwarg='pagina')),
    url(r'^list/books/sorted/$',
        views.BookList.as_view(ordering='name')),
    url(r'^list/books/sortedbypagesandnamedesc/$',
        views.BookList.as_view(ordering=('pages', '-name'))),
]
