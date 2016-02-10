# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from django.utils import six

from yepes.conf import settings
from yepes.loading import get_module, LoadingError, MissingClassError

BACKEND_PATHS = {

    # BUILT-IN MINIFIERS
    'css': 'yepes.utils.minifier.backends.css.minify',
    'html': 'yepes.utils.minifier.backends.html.minify',
    'js': 'yepes.utils.minifier.backends.js.minify',

    # THIRD-PARTY MINIFIERS
    'csscompressor': 'csscompressor.compress',
        # Yury Selivanov's Python port of the YUI CSS compression algorithm
        # (https://pypi.python.org/pypi/csscompressor).

    'cssmin': 'cssmin.cssmin',
        # Zachary Voase's Python port of the YUI CSS compression algorithm
        # (https://pypi.python.org/pypi/cssmin).

    'htmlmin': 'htmlmin.minify',
        # Python library htmlmin (https://pypi.python.org/pypi/htmlmin).

    'jsmin': 'jsmin.jsmin',
        # Python library jsmin (https://pypi.python.org/pypi/jsmin).

    'rcssmin': 'rcssmin.cssmin',
        # Python library rCSSmin (https://pypi.python.org/pypi/rcssmin).

    'rjsmin': 'rjsmin.jsmin',
        # Python library rJSmin (https://pypi.python.org/pypi/rjsmin).

    'slimit': 'slimit.minify',
        # Python library SlimIt (https://pypi.python.org/pypi/slimit).

}
_BACKENDS = {}
_REGISTERED = False


class MissingBackendError(LoadingError):

    def __init__(self, backend_name):
        msg = "Backend '{0}' could not be found."
        super(MissingBackendError, self).__init__(msg.format(backend_name))


def get_backend(name):
    if name in _BACKENDS:
        return _BACKENDS[name]
    else:
        if not _REGISTERED:
            _register_backends()

        if name in BACKEND_PATHS:
            _BACKENDS[name] = backend = _import_backend(BACKEND_PATHS[name])
            return backend
        else:
            raise MissingBackendError(name)


def has_backend(name):
    if name in _BACKENDS:
        return True
    else:
        if not _REGISTERED:
            _register_backends()

        return (name in BACKEND_PATHS)


def register_backend(name, path):
    if not _REGISTERED:
        _register_backends()
    _register_backend(name, path)


def _import_backend(path):
    module_path, class_name = path.rsplit('.', 1)
    module = get_module(module_path)
    class_ = getattr(module, class_name, None)
    if class_ is None:
        raise MissingClassError(class_name, module_path)
    else:
        return class_


def _register_backend(name, path):
    BACKEND_PATHS[name] = path
    _BACKENDS.pop(name)


def _register_backends():
    global _REGISTERED
    _REGISTERED = True
    if hasattr(settings, 'MINIFIER_BACKENDS'):
        for name, path in six.iteritems(settings.MINIFIER_BACKENDS):
            _register_backend(name, path)

