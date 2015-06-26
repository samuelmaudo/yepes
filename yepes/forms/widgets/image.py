# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from django.forms import widgets


class ImageWidget(widgets.ClearableFileInput):

    template_with_clear = (
        '<span class="clearable-file-input">'
          '%(clear)s'
          '<label for="%(clear_checkbox_id)s">'
            '%(clear_checkbox_label)s'
          '</label>'
        '</span>')

    template_with_initial = (
        '<table style="border:0 none;border-collapse:collapse">'
          '<tr>'
            '<td rowspan=2 style="border:0 none; padding:0">%(initial)s</td>'
            '<td style="border:0 none; height:36px; padding:0 10px">%(clear_template)s</td>'
          '</tr>'
          '<tr>'
            '<td style="border:0 none; padding:0 10px">%(input)s</td>'
          '</tr>'
        '</table>')

    url_markup_template = (
        '<a href="{0}" style="text-decoration:none">'
          '<img src="{0}" style="border:1px solid rgb(204, 204, 204);'
                               ' border-radius:3px;'
                               ' max-height:116px;'
                               ' max-width:116px">'
        '</a>')

