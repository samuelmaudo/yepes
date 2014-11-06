#!/usr/bin/env python
# -*- coding:utf-8 -*-

import logging
import os
import shutil
import sys
import tempfile

from django.utils import six
from django.utils._os import upath

ALWAYS_INSTALLED_APPS = [
    'mptt',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sites',
    'yepes',
    'yepes.apps.registry',
]

RUNTESTS_DIR = os.path.abspath(os.path.dirname(upath(__file__)))

SUBDIRS_TO_SKIP = [
    'requirements',
    'templates',
]

TEMP_DIR = tempfile.mkdtemp(prefix='yepes_')
os.environ['DJANGO_TEST_TEMP_DIR'] = TEMP_DIR

TEMPLATES_DIR = 'templates'


def get_test_modules():
    from django.db.models.loading import get_apps
    return [app.__name__.rsplit('.', 1)[0] for app in get_apps()]


def get_test_modules():
    modules = []
    for entry_name in os.listdir(RUNTESTS_DIR):
        if ('.' not in entry_name
                and entry_name != '__pycache__'
                and not entry_name.startswith('sql')
                and os.path.basename(entry_name) not in SUBDIRS_TO_SKIP
                and not os.path.isfile(entry_name)):
            modules.append(entry_name)

    return modules


def run_tests(verbosity, interactive, failfast, test_labels):
    from django.conf import settings
    from django.test.utils import get_runner

    state = setup(verbosity, test_labels)
    if not hasattr(settings, 'TEST_RUNNER'):
        settings.TEST_RUNNER = 'django.test.runner.DiscoverRunner'

    TestRunner = get_runner(settings)
    test_runner = TestRunner(
        verbosity=verbosity,
        interactive=interactive,
        failfast=failfast,
    )
    num_failures = test_runner.run_tests(test_labels or get_test_modules())
    teardown(state)
    return num_failures


def setup(verbosity, test_labels):
    from django.conf import settings
    from django.db.models.loading import get_apps, load_app
    from django.test.testcases import TransactionTestCase, TestCase

    # Force declaring available_apps in TransactionTestCase for faster tests.
    def no_available_apps(self):
        raise Exception('Please define available_apps in TransactionTestCase'
                        ' and its subclasses.')
    TransactionTestCase.available_apps = property(no_available_apps)
    TestCase.available_apps = None

    state = {
        'INSTALLED_APPS': settings.INSTALLED_APPS,
        'ROOT_URLCONF': getattr(settings, 'ROOT_URLCONF', ''),
        'TEMPLATE_DIRS': settings.TEMPLATE_DIRS,
        'LANGUAGE_CODE': settings.LANGUAGE_CODE,
        'STATIC_URL': settings.STATIC_URL,
        'STATIC_ROOT': settings.STATIC_ROOT,
    }

    # Redirect some settings for the duration of these tests.
    settings.INSTALLED_APPS = ALWAYS_INSTALLED_APPS
    settings.ROOT_URLCONF = 'urls'
    settings.STATIC_URL = '/static/'
    settings.STATIC_ROOT = os.path.join(TEMP_DIR, 'static')
    settings.TEMPLATE_DIRS = (os.path.join(RUNTESTS_DIR, TEMPLATES_DIR), )
    settings.LANGUAGE_CODE = 'en'
    settings.SITE_ID = 1

    if verbosity > 0:
        # Ensure any warnings captured to logging are piped through a verbose
        # logging handler. If any -W options were passed explicitly on command
        # line, warnings are not captured, and this has no effect.
        logger = logging.getLogger('py.warnings')
        handler = logging.StreamHandler()
        logger.addHandler(handler)

    # Load all the ALWAYS_INSTALLED_APPS.
    get_apps()

    # Load all the test model apps.
    test_modules = get_test_modules()

    # Reduce given test labels to just the app module path
    test_labels_set = set('.'.join(l.split('.')[:1]) for l in test_labels)

    # If the module (or an ancestor) was named on the command line,
    # or no modules were named (i.e., run all), import this module
    # and add it to INSTALLED_APPS.
    def found_in_labels(module_label):
        return any((module_label == label # Exact match
                    or module_label.startswith(label + '.')) # Ancestor match
                   for label
                   in test_labels_set)

    for module_label in test_modules:
        if not test_labels or found_in_labels(module_label):
            if verbosity >= 2:
                print('Importing application {0}'.format(module_label))
            module = load_app(module_label)
            if module and module_label not in settings.INSTALLED_APPS:
                settings.INSTALLED_APPS.append(module_label)

    return state


def teardown(state):
    from django.conf import settings

    try:
        # Removing the temporary TEMP_DIR. Ensure we pass in unicode
        # so that it will successfully remove temp trees containing
        # non-ASCII filenames on Windows. (We're assuming the temp dir
        # name itself does not contain non-ASCII characters.)
        shutil.rmtree(six.text_type(TEMP_DIR))
    except OSError:
        print('Failed to remove temp directory: {0}'.format(TEMP_DIR))

    # Restore the old settings.
    for key, value in state.items():
        setattr(settings, key, value)


if __name__ == '__main__':
    from optparse import OptionParser
    usage = '%prog [options] [module module module ...]'
    parser = OptionParser(usage=usage)
    parser.add_option(
        '-v', '--verbosity', action='store', dest='verbosity', default='1',
        type='choice', choices=['0', '1', '2', '3'],
        help='Verbosity level; 0=minimal output, 1=normal output, 2=all '
             'output')
    parser.add_option(
        '--noinput', action='store_false', dest='interactive', default=True,
        help='Tells Django to NOT prompt the user for input of any kind.')
    parser.add_option(
        '--failfast', action='store_true', dest='failfast', default=False,
        help='Tells Django to stop running the test suite after first failed '
             'test.')
    parser.add_option(
        '--settings',
        help='Python path to settings module, e.g. "myproject.settings". If '
             'this isn\'t provided, the DJANGO_SETTINGS_MODULE environment '
             'variable will be used.')

    options, args = parser.parse_args()
    if options.settings:
        os.environ['DJANGO_SETTINGS_MODULE'] = options.settings
    else:
        if 'DJANGO_SETTINGS_MODULE' not in os.environ:
            os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
        options.settings = os.environ['DJANGO_SETTINGS_MODULE']

    num_failures = run_tests(
        int(options.verbosity),
        options.interactive,
        options.failfast,
        args,
    )
    if num_failures > 0:
        sys.exit(True)

