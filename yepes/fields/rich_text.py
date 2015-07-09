# -*- coding:utf-8 -*-

from __future__ import unicode_literals

import re
try:
    import markdown2 as markdown
except ImportError:
    import markdown

from django.utils.translation import ugettext_lazy as _

from yepes import forms
from yepes.fields.text import TextField
from yepes.utils.deconstruct import clean_keywords

EMPTY_RE = re.compile(r'^\s*<(p|div)>\s*</\1>\s*$')


class HtmlGeneratorDescriptor(object):

    def __init__(self, field):
        self.text_attr = field.name
        self.html_generator = field.generate_html

    def __get__(self, obj, cls=None):
        if obj is None:
            return self
        else:
            return self.html_generator(getattr(obj, self.text_attr))


class RichTextField(TextField):

    description = _('Rich text')

    def __init__(self, *args, **kwargs):
        self.html_field = None
        self.processors = kwargs.pop('processors', ())
        self.store_html = kwargs.pop('store_html', True)
        super(RichTextField, self).__init__(*args, **kwargs)

    def contribute_to_class(self, cls, name):
        super(RichTextField, self).contribute_to_class(cls, name)
        html_attr = '{0}_html'.format(self.name)
        html_column = '{0}_html'.format(self.column)
        if not self.store_html:
            setattr(cls, html_attr, HtmlGeneratorDescriptor(self))
        elif self.html_field is None:
            self.html_field = TextField(
                editable=False,
                blank=True,
                null=False,
                db_column=html_column,
                verbose_name=self.verbose_name,
            )
            self.html_field.creation_counter = self.creation_counter + 0.1
            self.html_field.contribute_to_class(cls, html_attr)

    def deconstruct(self):
        name, path, args, kwargs = super(RichTextField, self).deconstruct()
        path = path.replace('yepes.fields.rich_text', 'yepes.fields')
        clean_keywords(self, kwargs, variables={
            'processors': (),
            'store_html': True,
        })
        return name, path, args, kwargs

    def formfield(self, **kwargs):
        kwargs['widget'] = forms.RichTextWidget()
        return super(RichTextField, self).formfield(**kwargs)

    def generate_html(self, text):
        if not text:
            return ''

        html = markdown.markdown(text)
        if EMPTY_RE.search(html):
            return ''

        for processor in self.processors:
            html = processor(html)

        return html

    def pre_save(self, model_instance, add):
        text = super(RichTextField, self).pre_save(model_instance, add)
        if self.store_html:
            html = self.generate_html(text)
            html_attr = self.html_field.name
            setattr(model_instance, html_attr, html)

        return text

    def save_form_data(self, instance, data):
        super(RichTextField, self).save_form_data(instance, data)
        if self.store_html:
            html = self.generate_html(data)
            html_attr = self.html_field.name
            setattr(instance, html_attr, html)

