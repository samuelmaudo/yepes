# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from lxml import etree
import os

from django.template.base import Library, TemplateSyntaxError
from django.utils.encoding import force_str

from yepes.conf import settings
from yepes.template import SingleTag

register = Library()


def render(source, method='svg'):

    svg = etree.Element('svg')
    for element in source.iterchildren():
        i = element.tag.find('}')
        if i >= 0:
            element.tag = element.tag[i+1:]

        element.tail = None
        svg.append(element)

    if method == 'img':

        measures = ''
        if 'viewBox' in source.attrib:
            viewBox = source.attrib['viewBox'].split()
            if len(viewBox) == 4 and viewBox[2].isdigit() and viewBox[3].isdigit():
                svg.attrib['viewBox'] = ' '.join(viewBox)
                measures = ' width="{0}" height="{1}"'.format(viewBox[2], viewBox[3])

        svg.attrib['xmlns'] = 'http://www.w3.org/2000/svg'
        code = etree.tostring(svg, encoding='utf8', pretty_print=False).strip()
        code = code.replace('"', "'")
        code = code.replace('<', '%3C')
        code = code.replace('>', '%3E')
        code = code.replace('#', '%23')
        return '<img src="data:image/svg+xml;charset=utf8,{0}"{1}>'.format(code, measures)

    elif method == 'svg':

        if 'viewBox' in source.attrib:
            viewBox = source.attrib['viewBox'].split()
            if len(viewBox) == 4 and viewBox[2].isdigit() and viewBox[3].isdigit():
                svg.attrib['width'] = viewBox[2]
                svg.attrib['height'] = viewBox[3]

        return etree.tostring(svg, encoding='utf8', pretty_print=True).strip()

    else:

        return ''


## {% insert_file file_name[ method] %} ########################################


class InsertFileTag(SingleTag):

    def process(self, file_name, method='svg'):
        if method not in ('svg', 'img'):
            msg = "'{0}' tag does not support '{1}' method."
            raise TemplateSyntaxError(msg.format(self.tag_name, method))

        root = None
        for dir_name in settings.STATICFILES_DIRS:
            try:
                file = open(os.path.join(dir_name, file_name))
            except IOError:
                continue
            else:
                root = etree.fromstring(force_str(file.read()))
                file.close()
                break

        if root is None or not root.tag.endswith('svg'):
            return ''

        return render(root, method)

register.tag('insert_file', InsertFileTag.as_tag())


## {% insert_symbol file_name symbol_name[ method] %} ##########################


class InsertSymbolTag(SingleTag):

    def process(self, file_name, symbol_name, method='svg'):
        if method not in ('svg', 'img'):
            msg = "'{0}' tag does not support '{1}' method."
            raise TemplateSyntaxError(msg.format(self.tag_name, method))

        root = None
        for dir_name in settings.STATICFILES_DIRS:
            try:
                file = open(os.path.join(dir_name, file_name))
            except IOError:
                continue
            else:
                root = etree.fromstring(force_str(file.read()))
                file.close()
                break

        if root is None or not root.tag.endswith('svg'):
            return ''

        defs = None
        for element in root.iterchildren():
            if element.tag.endswith('defs'):
                defs = element
                break

        if defs is None:
            return ''

        symbol = None
        for element in defs.iterchildren():
            if (not isinstance(element, etree._Comment)
                    and element.tag.endswith('symbol')
                    and element.attrib.get('id') == symbol_name):
                symbol = element
                break

        if symbol is None:
            return ''

        return render(symbol, method)

register.tag('insert_symbol', InsertSymbolTag.as_tag())

