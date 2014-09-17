# -*- coding:utf-8 -*-

from __future__ import unicode_literals

import mimetypes
import os
from wsgiref.util import FileWrapper

from django.core.exceptions import ImproperlyConfigured
from django.http import Http404, HttpResponse
from django.utils.translation import ugettext as _
from django.views.generic import View

from yepes.conf import settings


class StaticFileView(View):

    encoding = None
    filename = None
    mimetype = None

    def get(self, request, *args, **kwargs):
        filename = self.get_filename().format(
            filename=self.kwargs.get('filename', ''),
            media=settings.MEDIA_ROOT,
            static=settings.STATIC_ROOT,
        )
        mimetype = self.get_mimetype(filename)
        encoding = self.get_encoding(filename)

        try:
            file = open(filename, 'rb')
        except IOError:
            msg = _('No {verbose_name} found matching the query')
            raise Http404(msg.format(verbose_name=_('file')))

        wrapper = FileWrapper(file)
        response = HttpResponse(wrapper)
        response['Content-Type'] = mimetype or 'application/octet-stream'
        response['Content-Length'] = os.path.getsize(filename)
        if encoding:
            response['Content-Encoding'] = encoding

        return response

    def get_encoding(self, filename):
        if not self.encoding:
            return mimetypes.guess_type(filename)[1]
        else:
            return self.encoding

    def get_filename(self):
        if not self.filename:
            msg = ('{cls} is missing a filename.'
                    ' Define {cls}.filename'
                    ' or override {cls}.get_filename().')
            raise ImproperlyConfigured(msg.format(cls=self.__class__.__name__))
        else:
            return self.filename

    def get_mimetype(self, filename):
        if not self.mimetype:
            return mimetypes.guess_type(filename)[0]
        else:
            return self.mimetype

