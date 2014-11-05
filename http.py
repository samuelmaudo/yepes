# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from django.http import HttpResponse

from yepes.utils import json


class JsonResponse(HttpResponse):
    """
    An HTTP response class that consumes data to be serialized to JSON.

    :param data: Data to be dumped into json. By default only ``dict`` objects
      are allowed to be passed due to a security flaw before EcmaScript 5. See
      the ``safe`` parameter for more information.
    :param encoder: Should be an json encoder class. Defaults to
      ``yepes.utils.json.JSONEncoder``.
    :param indent: Controls the indent level of the JSON array elements and
      object members. Defaults to ``None`` that means that no indentation or
      line break will be printed.
    :param safe: Controls if only ``dict`` objects may be serialized. Defaults
      to ``True``.

    """
    def __init__(self, data, encoder=json.JSONEncoder, indent=None, safe=True,
                 **kwargs):
        if safe and not isinstance(data, dict):
            raise TypeError('In order to allow non-dict objects to be '
                            'serialized set the safe parameter to False')

        kwargs.setdefault('content_type', 'application/json; charset=utf-8')
        data = json.dumps(data, cls=encoder, indent=indent)
        super(JsonResponse, self).__init__(content=data, **kwargs)

