# -*- coding:utf-8 -*-

from django.conf.urls import patterns, include, url

from yepes.views import CacheStatsView

urlpatterns = patterns('',
    url(r'^cache/', CacheStatsView.as_view(), name='cache_stats'),
)
