# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from django.core.files.storage import FileSystemStorage
from django.views.generic import TemplateView

from yepes.apps import apps
from yepes.views import ListView

Configuration = apps.get_model('thumbnails', 'Configuration')
SourceFile = apps.get_class('thumbnails.files', 'SourceFile')


class TestMixin(object):

    def get_context_data(self, **kwargs):
        context = super(TestMixin, self).get_context_data(**kwargs)
        context['source'] = self.get_source_file()
        return context

    def get_source_file(self):
        app_config = apps.get_app_config('thumbnails')
        app_static_dir = os.path.join(app_config.path, 'static')
        app_storage = FileSystemStorage(app_static_dir)
        media_storage = FileSystemStorage()
        path = 'thumbnails/wolf.jpg'
        if not media_storage.exists(path):
            media_storage.save(path, app_storage.open(path))
        elif app_storage.modified_time(path) > media_storage.modified_time(path):
            media_storage.delete(path)
            media_storage.save(path, app_storage.open(path))

        return SourceFile(media_storage.open(path), path, media_storage)


class ConfigurationsTestView(TestMixin, ListView):

    model = Configuration
    template_name = 'thumbnails/configurations.html'


class OptionsTestView(TestMixin, TemplateView):

    template_name = 'thumbnails/options.html'

