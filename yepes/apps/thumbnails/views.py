# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from django.contrib.staticfiles.storage import AppStaticStorage

from yepes.apps.thumbnails.files import SourceFile
from yepes.conf import settings
from yepes.loading import get_model
from yepes.views import ListView

Configuration = get_model('thumbnails', 'Configuration')


class TestView(ListView):

    model = Configuration
    template_name = 'thumbnails/test.html'

    def get_context_data(self, **kwargs):
        context = super(TestView, self).get_context_data(**kwargs)
        context['source'] = self.get_source_file()
        return context

    def get_source_file(self):
        storage = AppStaticStorage('yepes.apps.thumbnails', settings.STATIC_URL)
        filename = 'thumbnails/test.jpg'
        file = storage.open(filename)
        return SourceFile(file, filename, storage)

