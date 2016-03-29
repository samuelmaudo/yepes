# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from django.conf.urls import patterns, include, url

from .views import ArticleDetailView

urlpatterns = patterns('',
    url(r'^(?P<slug>[-\w]+)\.html$',
        ArticleDetailView.as_view(),
        name='article_detail',
    ),
)
