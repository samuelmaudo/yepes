# -*- coding:utf-8 -*-

from yepes.apps import apps

AbstractConfiguration = apps.get_class('thumbnails.abstract_models', 'AbstractConfiguration')
AbstractSource = apps.get_class('thumbnails.abstract_models', 'AbstractSource')
AbstractThumbnail = apps.get_class('thumbnails.abstract_models', 'AbstractThumbnail')


class Configuration(AbstractConfiguration):
    pass

class Source(AbstractSource):
    pass

class Thumbnail(AbstractThumbnail):
    pass

