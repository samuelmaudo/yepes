# -*- coding:utf-8 -*-

from django.conf.urls import patterns, include, url

from yepes.apps import apps

ConfigurationsTestView = apps.get_class('thumbnails.views', 'ConfigurationsTestView')
OptionsTestView = apps.get_class('thumbnails.views', 'OptionsTestView')


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
