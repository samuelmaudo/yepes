# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from django.contrib.staticfiles.storage import AppStaticStorage
from django.core.files.storage import FileSystemStorage
from django.views.generic import TemplateView

from yepes.conf import settings
from yepes.contrib.thumbnails.files import SourceFile
from yepes.loading import get_model
from yepes.views import ListView

Configuration = get_model('thumbnails', 'Configuration')


class TestMixin(object):

    def get_context_data(self, **kwargs):
        context = super(TestMixin, self).get_context_data(**kwargs)
        context['source'] = self.get_source_file()
        return context

    def get_source_file(self):
        app = AppStaticStorage('yepes.contrib.thumbnails')
        media = FileSystemStorage(settings.MEDIA_ROOT, settings.MEDIA_URL)
        path = 'thumbnails/wolf.jpg'
        if not media.exists(path):
            media.save(path, app.open(path))
        elif app.modified_time(path) > media.modified_time(path):
            media.delete(path)
            media.save(path, app.open(path))

        return SourceFile(media.open(path), path, media)


class ConfigurationsTestView(TestMixin, ListView):

    model = Configuration
    template_name = 'thumbnails/configurations.html'


class OptionsTestView(TestMixin, TemplateView):

    template_name = 'thumbnails/options.html'

