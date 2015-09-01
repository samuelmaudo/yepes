# -*- coding:utf-8 -*-

from django.conf.urls import patterns, include, url

from yepes.loading import get_class

ConfigurationsTestView = get_class('thumbnails.views', 'ConfigurationsTestView')
OptionsTestView = get_class('thumbnails.views', 'OptionsTestView')


urlpatterns = patterns('',
    url(r'^configurations/$',
        ConfigurationsTestView.as_view(),
        name='thumbnail_configurations',
    ),
    url(r'^options/$',
        OptionsTestView.as_view(),
        name='thumbnail_options',
    ),
)
