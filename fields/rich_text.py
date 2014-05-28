# -*- coding:utf-8 -*-

from __future__ import unicode_literals

import re
try:
    import markdown2 as markdown
except ImportError:
    import markdown

from django.db import models

from yepes.forms.widgets import RichTextWidget

EMPTY_RE = re.compile(r'^\s*<(p|div)>\s*</\1>\s*$')


class RichTextField(models.TextField):

    html_field = None

    def __init__(self, *args, **kwargs):
        self.processors = kwargs.pop('processors', ())
        super(RichTextField, self).__init__(*args, **kwargs)

    def formfield(self, **kwargs):
        kwargs['widget'] = RichTextWidget()
        return super(RichTextField, self).formfield(**kwargs)

    def contribute_to_class(self, cls, name):
        super(RichTextField, self).contribute_to_class(cls, name)
        if self.html_field is None:
            self.html_field = models.TextField(
                editable=False,
                blank=True,
                null=False,
                db_column='{0}_html'.format(self.column),
                verbose_name=self.verbose_name,
            )
            self.html_field.creation_counter = self.creation_counter + 0.1
            self.html_field.contribute_to_class(cls, '{0}_html'.format(self.name))

    def pre_save(self, model_instance, add):
        text = super(RichTextField, self).pre_save(model_instance, add)
        if not text:
            html = ''
        else:
            html = markdown.markdown(text)
            if EMPTY_RE.search(html):
                html = ''
            else:
                for processor in self.processors:
                    html = processor(html)

        setattr(model_instance, self.html_field.attname, html)
        return text

    def south_field_triple(self):
        """
        Returns a suitable description of this field for South.
        """
        from south.modelsinspector import introspector
        field_class = 'django.db.models.fields.TextField'
        args, kwargs = introspector(self)
        return (field_class, args, kwargs)

