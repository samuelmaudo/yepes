# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _

from yepes.apps.registry import Registry
from yepes.apps.registry.fields import *


registry = Registry(namespace='core')
registry.register(
    'ALLOWED_SUBDOMAINS',
    CommaSeparatedField(
        initial = (),
        label = _('Allowed subdomains'),
        max_length = 255,
        required = False,
))
registry.register(
    'BANNED_IP_ADDRESSES',
    CommaSeparatedField(
        initial = (),
        label = _('Banned IP addresses'),
        max_length = 255,
        required = False,
))
registry.register(
    'DEFAULT_SUBDOMAIN',
    CharField(
        initial = '',
        label = _('Default subdomain'),
        max_length = 15,
        required = False,
))
registry.register(
    'STOP_WORDS',
    CommaSeparatedField(
        initial = (
            'de',
            'la',
            'que',
            'el',
            'en',
            'y',
            'a',
            'los',
            'del',
            'se',
            'las',
            'por',
            'un',
            'para',
            'con',
            'no',
            'una',
            'su',
            'al',
            'es',
            'lo',
            'como',
            'más',
            'pero',
            'sus',
            'le',
            'ya',
            'o',
            'fue',
            'este',
            'ha',
            'sí',
            'porque',
            'esta',
            'son',
            'entre',
            'está',
            'cuando',
            'muy',
            'sin',
            'sobre',
            'ser',
            'tiene',
            'también',
            'me',
            'hasta',
            'hay',
            'donde',
            'han',
            'quien',
            'están',
            'estado',
            'desde',
            'todo',
            'nos',
            'durante',
            'estados',
            'todos',
            'uno',
            'les',
            'ni',
            'contra',
            'otros',
            'fueron',
            'ese',
            'eso',
            'había',
            'ante',
            'ellos',
            'e',
            'esto',
            'mí',
            'antes',
            'algunos',
            'qué',
            'unos',
            'yo',
            'otro',
            'otras',
            'otra',
            'él',
            'tanto',
            'esa',
            'estos',
            'mucho',
            'quienes',
            'nada',
            'muchos',
            'cual',
            'sea',
            'poco',
            'ella',
            'estar',
            'haber',
            'estas',
            'estaba',
            'estamos',
            'algunas',
            'algo',
            'nosotros',
        ),
        label = _('Stop words'),
        required = False,
))

