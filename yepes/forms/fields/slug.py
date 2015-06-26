# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from yepes.forms.fields.char import CharField
from yepes.utils import slugify


class SlugField(CharField):

    def __init__(self, *args, **kwargs):
        kwargs['normalize_spaces'] = False
        kwargs['trim_spaces'] = False
        super(SlugField, self).__init__(*args, **kwargs)

    def to_python(self, *args, **kwargs):
        value = super(SlugField, self).to_python(*args, **kwargs)
        if value:
            return slugify(value)
        else:
            return value

