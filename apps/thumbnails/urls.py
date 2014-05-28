# -*- coding:utf-8 -*-

from django.conf.urls import patterns, include, url

from yepes.loading import get_class

TestView = get_class('thumbnails.views', 'TestView')


urlpatterns = patterns('',
    url(r'^test/$',
        TestView.as_view(),
        name='thumbnail_test',
    ),
)
