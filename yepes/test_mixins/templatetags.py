# -*- coding:utf-8 -*-

from __future__ import unicode_literals

import re

from django.template import Context, Template, TemplateSyntaxError
from django.utils import six

from yepes.template import DoubleTag, TagSyntaxError

TAG_NAME_RE = re.compile(r'^\{% ([_a-z]+)')


class TemplateTagsMixin(object):

    requiredLibraries = None

    def checkSyntax(self, tag_class, expected_syntax):
        tag_name = TAG_NAME_RE.search(expected_syntax).group(1)
        self.assertEqual(
            expected_syntax,
            tag_class.get_syntax(tag_name),
        )
        error_text = 'Correct syntax is {0}'.format(expected_syntax)
        self.assertEqual(
            error_text,
            six.text_type(TagSyntaxError(tag_class, tag_name)),
        )
        erroneous_args = ''
        process = tag_class.get_process_arguments()
        if len(process.args) - len(process.defaults or ()) == 1:
            if not process.keywords:
                erroneous_args = " acxz='acxz'"
            elif not process.varargs:
                erroneous_args = ''.join(" 'acxz'" * (len(process.args)))
            else:
                return  # There is no erroneous arguments.

        template_code = ''
        if self.requiredLibraries is not None:
            for library in self.requiredLibraries:
                template_code += '{{% load {0} %}}\n'.format(library)

        template_code += '{{% {0}{1} %}}\n'.format(tag_name, erroneous_args)
        if issubclass(tag_class, DoubleTag):
            template_code += '{{% end{0} %}}\n'.format(tag_name)

        self.assertNotValidSyntax(template_code, error_text)

    def assertValidSyntax(self, template_code):
        try:
            Template(template_code)
        except TemplateSyntaxError as error:
            raise self.failureException(six.text_type(error))
        except:
            pass
        else:
            pass

    def assertNotValidSyntax(self, template_code, error_text=None):
        try:
            Template(template_code)
        except TemplateSyntaxError as error:
            if error_text is not None:
                self.assertEqual(error_text, six.text_type(error))
        except:
            raise self.failureException('Syntax is valid')
        else:
            raise self.failureException('Syntax is valid')

