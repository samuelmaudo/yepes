# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from django.conf.urls import url

from .views import ArticleDetailView

urlpatterns = [
    url(r'^(?P<slug>[-\w]+)\.html$',
        ArticleDetailView.as_view(),
        name='article_detail',
    ),
]
