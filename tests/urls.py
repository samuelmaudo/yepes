# -*- coding:utf-8 -*-

from django.conf.urls import url

from yepes.views import CacheStatsView

urlpatterns = [
    url(r'^cache/', CacheStatsView.as_view(), name='cache_stats'),
]
