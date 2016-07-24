# -*- coding:utf-8 -*-

from django.conf.urls import url

from yepes.apps import apps

ConfigurationsTestView = apps.get_class('thumbnails.views', 'ConfigurationsTestView')
OptionsTestView = apps.get_class('thumbnails.views', 'OptionsTestView')


urlpatterns = [
    url(r'^configurations/$',
        ConfigurationsTestView.as_view(),
        name='thumbnail_configurations',
    ),
    url(r'^options/$',
        OptionsTestView.as_view(),
        name='thumbnail_options',
    ),
]
