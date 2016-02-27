# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from lxml import etree
from posixpath import normpath

from django.contrib.staticfiles import finders as staticfiles_finders
from django.contrib.staticfiles.storage import staticfiles_storage
from django.core.cache import get_cache
from django.template.base import Library, TemplateSyntaxError
from django.utils.encoding import force_bytes, force_text

from yepes.conf import settings
from yepes.template import SingleTag

SYMBOL_CACHE = get_cache('django.core.cache.backends.locmem.LocMemCache', **{
    'LOCATION': 'yepes.templatetags.svg.insert_symbol',
    'TIMEOUT': 600,
})

register = Library()


class SvgMixin(object):

    def generate_code(self, source, method='svg'):
        svg = etree.Element('svg')
        for element in source.iterchildren():
            i = element.tag.find('}')
            if i >= 0:
                element.tag = element.tag[i+1:]

            element.tail = None
            svg.append(element)

        width = ''
        height = ''
        if 'width' in source.attrib and 'height' in source.attrib:
            w = source.attrib['width']
            h = source.attrib['height']
            if w.isdigit() and h.isdigit():
                width = w
                height = h

        elif 'viewBox' in source.attrib:
            viewBox = source.attrib['viewBox'].split()
            if len(viewBox) == 4:
                w = viewBox[2]
                h = viewBox[3]
                if w.isdigit() and h.isdigit():
                    width = w
                    height = h

        if method == 'img':

            measures = ''
            if width and height:
                measures = ' width="{0}" height="{1}"'.format(width, height)

            svg.attrib['xmlns'] = 'http://www.w3.org/2000/svg'
            code = force_text(etree.tostring(
                svg,
                encoding='utf8',
                pretty_print=False,
            )).strip()
            code = code.replace('"', "'")
            code = code.replace('<', '%3C')
            code = code.replace('>', '%3E')
            code = code.replace('#', '%23')
            return '<img src="data:image/svg+xml;charset=utf8,{0}"{1}>'.format(code, measures)

        if method == 'svg':

            if width and height:
                svg.attrib['width'] = width
                svg.attrib['height'] = height

            return force_text(etree.tostring(
                svg,
                encoding='utf8',
                pretty_print=True)
            ).strip()

        return ''

    def open_file(self, file_name):
        file_name = normpath(file_name)
        if file_name:
            try:
                return staticfiles_storage.open(file_name)
            except IOError:
                if settings.DEBUG:
                    file_path = staticfiles_finders.find(file_name)
                    if file_path:
                        try:
                            return open(file_path)
                        except IOError:
                            pass

        return None

    def parse_file(self, file_name):
        file = self.open_file(file_name)
        if file is None:
            return file

        try:
            root = etree.fromstring(force_bytes(file.read()))
        finally:
            file.close()

        return root


## {% insert_file file_name[ method] %} ########################################


class InsertFileTag(SvgMixin, SingleTag):

    def process(self, file_name, method='svg'):
        if method not in ('svg', 'img'):
            msg = "'{0}' tag does not support '{1}' method."
            raise TemplateSyntaxError(msg.format(self.tag_name, method))

        root = self.parse_file(file_name)
        if root is None or not root.tag.endswith('svg'):
            return ''

        return self.generate_code(root, method)

register.tag('insert_file', InsertFileTag.as_tag())


## {% insert_symbol file_name symbol_name[ method] %} ##########################


class InsertSymbolTag(SvgMixin, SingleTag):

    def process(self, file_name, symbol_name, method='svg'):
        if method not in ('svg', 'img'):
            msg = "'{0}' tag does not support '{1}' method."
            raise TemplateSyntaxError(msg.format(self.tag_name, method))

        cache = SYMBOL_CACHE.get(file_name)
        if cache is None:
            cache = {}

            root = self.parse_file(file_name)
            if root is not None and root.tag.endswith('svg'):

                defs = None
                for element in root.iterchildren():
                    if element.tag.endswith('defs'):
                        defs = element
                        break

                if defs is not None:
                    cache = {
                        element.attrib.get('id'): force_bytes(etree.tostring(
                            element,
                            encoding='utf8',
                            pretty_print=False
                        ))
                        for element
                        in defs.iterchildren()
                        if not isinstance(element, etree._Comment)
                        and element.tag.endswith('symbol')
                    }

            SYMBOL_CACHE.set(file_name, cache)

        symbol_xml = cache.get(symbol_name)
        if symbol_xml is None:
            return ''

        return self.generate_code(etree.fromstring(symbol_xml), method)

register.tag('insert_symbol', InsertSymbolTag.as_tag())

