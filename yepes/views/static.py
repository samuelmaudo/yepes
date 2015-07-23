# -*- coding:utf-8 -*-

from __future__ import unicode_literals

import mimetypes
import os
import re
import stat

from django.core.exceptions import ImproperlyConfigured
from django.http import (
    CompatibleStreamingHttpResponse,
    Http404,
    HttpResponseNotModified,
)
from django.utils.http import http_date, parse_http_date
from django.utils.translation import ugettext as _
from django.views.generic import View

from yepes.conf import settings

HTTP_IF_MODIFIED_SINCE_RE = re.compile(
    r'^([^;]+)(; length=([0-9]+))?$',
    re.IGNORECASE,
)

class StaticFileView(View):

    charset = None
    encoding = None
    filename = None
    mimetype = None

    def get(self, request, *args, **kwargs):
        filename = self.get_filename().format(
            filename=self.kwargs.get('filename', ''),
            media=settings.MEDIA_ROOT,
            static=settings.STATIC_ROOT,
        )
        if not os.path.exists(filename) or os.path.isdir(filename):
            raise Http404(_('No file found matching the query'))

        filestats = os.stat(filename)
        if not self.was_modified(filename, filestats):
            return HttpResponseNotModified()

        try:
            fileobj = open(filename, 'rb')
        except IOError:
            raise Http404(_('No file found matching the query'))

        charset = self.get_charset(filename, filestats)
        mimetype = self.get_mimetype(filename, filestats)
        encoding = self.get_encoding(filename, filestats)
        if not charset and mimetype and not mimetype.startswith('text'):
            content_type = mimetype or 'application/octet-stream'
        else:
            content_type = '{0}; charset={1}'.format(
                mimetype or settings.DEFAULT_CONTENT_TYPE,
                charset or settings.DEFAULT_CHARSET,
            )
        response = CompatibleStreamingHttpResponse(fileobj, content_type)
        response['Last-Modified'] = http_date(filestats.st_mtime)
        if stat.S_ISREG(filestats.st_mode):
            response['Content-Length'] = filestats.st_size
        if encoding:
            response['Content-Encoding'] = encoding

        return response

    def get_charset(self, filename, filestats):
        return self.charset

    def get_encoding(self, filename, filestats):
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

    def get_mimetype(self, filename, filestats):
        if not self.mimetype:
            return mimetypes.guess_type(filename)[0]
        else:
            return self.mimetype

    def was_modified(self, filename, filestats):
        header = self.request.META.get('HTTP_IF_MODIFIED_SINCE')
        if header is None:
            return True

        matchobj = HTTP_IF_MODIFIED_SINCE_RE.search(header)
        if matchobj is None:
            return True

        try:
            header_mtime = parse_http_date(matchobj.group(1))
            header_size = int(matchobj.group(3) or 0)
        except (AttributeError, ValueError, OverflowError):
            return True

        if header_size and header_size != filestats.st_size:
            return True

        if filestats.st_mtime > header_mtime:
            return True

        return False

