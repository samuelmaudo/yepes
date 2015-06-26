# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from django.forms import widgets
from django.forms.util import flatatt
from django.utils.encoding import force_text
from django.utils.html import format_html


class RichTextWidget(widgets.Textarea):

    class Media:
        css = {'all': ['rich_text/widget.css']}
        js = ['rich_text/pagedown.js', 'rich_text/widget.js']

    def build_attrs(self, *args, **kwargs):
        attrs = super(RichTextWidget, self).build_attrs(*args, **kwargs)
        attrs['class'] = 'mdEditorTextArea'
        return attrs

    def render(self, name, value, attrs=None):
        return format_html("""
            <div class="mdEditorFrame">
              <div class="mdEditorWindow">
                <div class="mdEditorCanvas">
                  <textarea{0}>\r\n{1}</textarea>
                  <div class="mdEditorSeparator"></div>
                  <div class="mdEditorPreview"></div>
                </div>
              </div>
            </div>""",
            flatatt(self.build_attrs(attrs, name=name)),
            force_text(value) if value is not None else '')

