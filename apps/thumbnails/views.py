# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from django.contrib.staticfiles.finders import find as find_file
from django.contrib.staticfiles.storage import AppStaticStorage
from django.utils import six
from django.utils.itercompat import is_iterable

from yepes.apps.thumbnails.files import SourceFile
from yepes.conf import settings
from yepes.loading import get_model
from yepes.views import ListView

Configuration = get_model('thumbnails', 'Configuration')


class TestView(ListView):

    model = Configuration

    def get_context_data(self, **kwargs):
        context = super(TestView, self).get_context_data(**kwargs)
        storage = AppStaticStorage('yepes.apps.thumbnails', settings.STATIC_URL)
        filename = 'thumbnails/test.jpg'
        file = storage.open(filename)
        context['source'] = SourceFile(file, filename, storage)
        return context

    def get_template_names(self):
        names = []
        if isinstance(self.template_name, six.string_types):
            names.append(self.template_name)
        elif is_iterable(self.template_name):
            names.extend(self.template_name)

        model = self.get_model()
        if model is not None:
            names.append('{0}/test.html'.format(model._meta.app_label))

        return names

