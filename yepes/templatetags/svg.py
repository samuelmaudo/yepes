# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from lxml import etree
from posixpath import normpath

from django.contrib.staticfiles import finders as staticfiles_finders
from django.contrib.staticfiles.storage import staticfiles_storage
from django.core.cache import caches, DEFAULT_CACHE_ALIAS
from django.template import Library, TemplateSyntaxError
from django.utils.encoding import force_bytes, force_text

from yepes.conf import settings
from yepes.template import SingleTag

register = Library()


class SvgMixin(object):

    def generate_code(self, source, method='svg'):
        svg = etree.Element('svg')
        for element in source.iterchildren():
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

        for element in root.iter():
            i = element.tag.find('}')
            if i >= 0:
                element.tag = element.tag[i+1:]

            if element.text is not None:
                element.text = element.text.strip()

            element.tail = None

        return self.generate_code(root, method)

register.tag('insert_file', InsertFileTag.as_tag())


## {% insert_symbol file_name symbol_name[ method] %} ##########################


class InsertSymbolTag(SvgMixin, SingleTag):

    def process(self, file_name, symbol_name, method='svg'):
        if method not in ('svg', 'img'):
            msg = "'{0}' tag does not support '{1}' method."
            raise TemplateSyntaxError(msg.format(self.tag_name, method))

        symbols = self.retrieve_symbol_definitions(file_name)
        if symbols is None:
            symbols = {}

            root = self.parse_file(file_name)
            if root is not None and root.tag.endswith('svg'):

                defs = None
                for element in root.iterchildren():
                    if element.tag.endswith('defs'):
                        defs = element
                        break

                if defs is not None:
                    for symb in defs.iterchildren():
                        if (isinstance(symb, etree._Comment)
                                or not symb.tag.endswith('symbol')):
                            continue

                        symbol = etree.Element('symbol')
                        symbol.attrib['id'] = symb.attrib['id']
                        if 'width' in symb.attrib:
                            symbol.attrib['width'] = symb.attrib['width']

                        if 'height' in symb.attrib:
                            symbol.attrib['height'] = symb.attrib['height']

                        if 'viewBox' in symb.attrib:
                            symbol.attrib['viewBox'] = symb.attrib['viewBox']

                        for element in symb.iterchildren():
                            for elem in element.iter():
                                i = elem.tag.find('}')
                                if i >= 0:
                                    elem.tag = elem.tag[i+1:]

                                if elem.text is not None:
                                    elem.text = elem.text.strip()

                                elem.tail = None

                            symbol.append(element)

                        xml = force_bytes(etree.tostring(
                            symbol,
                            encoding='utf8',
                            pretty_print=False
                        ))
                        symbols[symbol.attrib['id']] = xml

            self.store_symbol_definitions(file_name, symbols)

        symbol_xml = symbols.get(symbol_name)
        if symbol_xml is None:
            return ''

        return self.generate_code(etree.fromstring(symbol_xml), method)

    def retrieve_symbol_definitions(self, key):
        cache = caches[DEFAULT_CACHE_ALIAS]
        new_key = '.'.join(('yepes.templatetags.svg.insert_symbol', key))
        return cache.get(new_key)

    def store_symbol_definitions(self, key, symbols):
        cache = caches[DEFAULT_CACHE_ALIAS]
        new_key = '.'.join(('yepes.templatetags.svg.insert_symbol', key))
        cache.set(new_key, symbols, timeout=600)

register.tag('insert_symbol', InsertSymbolTag.as_tag())

