#!/usr/bin/env python
# -*- coding:utf-8 -*-

import logging
import os
import shutil
import subprocess
import sys
import tempfile
import warnings

from django.utils import six
from django.utils._os import upath

ALWAYS_INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sites',
    'mptt',
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


def bisect_tests(bisection_label, options, test_labels):
    state = setup(int(options.verbosity), test_labels)

    test_labels = test_labels or get_test_modules()

    print('***** Bisecting test suite: {0}'.format(' '.join(test_labels)))

    # Make sure the bisection point isn't in the test list
    # Also remove tests that need to be run in specific combinations
    for label in [bisection_label, 'model_inheritance_same_model_name']:
        try:
            test_labels.remove(label)
        except ValueError:
            pass

    subprocess_args = [
        sys.executable,
        upath(__file__),
        '--settings={0}'.format(options.settings),
    ]
    if options.failfast:
        subprocess_args.append('--failfast')
    if options.verbosity:
        subprocess_args.append('--verbosity={0}'.format(options.verbosity))
    if not options.interactive:
        subprocess_args.append('--noinput')

    iteration = 1
    while len(test_labels) > 1:
        midpoint = len(test_labels)/2
        test_labels_a = test_labels[:midpoint] + [bisection_label]
        test_labels_b = test_labels[midpoint:] + [bisection_label]
        print('***** Pass {0}a: Running the first half of the test suite'.format(iteration))
        print('***** Test labels: {0}'.format(' '.join(test_labels_a)))
        failures_a = subprocess.call(subprocess_args + test_labels_a)

        print('***** Pass {0}b: Running the second half of the test suite'.format(iteration))
        print('***** Test labels: {0}'.format(' '.join(test_labels_b)))
        print('')
        failures_b = subprocess.call(subprocess_args + test_labels_b)

        if failures_a and not failures_b:
            print('***** Problem found in first half. Bisecting again...')
            iteration = iteration + 1
            test_labels = test_labels_a[:-1]
        elif failures_b and not failures_a:
            print('***** Problem found in second half. Bisecting again...')
            iteration = iteration + 1
            test_labels = test_labels_b[:-1]
        elif failures_a and failures_b:
            print('***** Multiple sources of failure found')
            break
        else:
            print('***** No source of failure found... try pair execution (--pair)')
            break

    if len(test_labels) == 1:
        print('***** Source of error: {0}'.format(test_labels[0]))
    teardown(state)


def paired_tests(paired_test, options, test_labels):
    state = setup(int(options.verbosity), test_labels)

    test_labels = test_labels or get_test_modules()

    print('***** Trying paired execution')

    # Make sure the constant member of the pair isn't in the test list
    # Also remove tests that need to be run in specific combinations
    for label in [paired_test, 'model_inheritance_same_model_name']:
        try:
            test_labels.remove(label)
        except ValueError:
            pass

    subprocess_args = [
        sys.executable,
        upath(__file__),
        '--settings={0}'.format(options.settings),
    ]
    if options.failfast:
        subprocess_args.append('--failfast')
    if options.verbosity:
        subprocess_args.append('--verbosity={0}'.format(options.verbosity))
    if not options.interactive:
        subprocess_args.append('--noinput')

    for i, label in enumerate(test_labels):
        print('***** {0} of {1}: Check test pairing with {2}'.format(
              i + 1, len(test_labels), label))
        failures = subprocess.call(subprocess_args + [label, paired_test])
        if failures:
            print('***** Found problem pair with {0}'.format(label))
            return

    print('***** No problem pair found')
    teardown(state)


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
    parser.add_option(
        '--bisect', action='store', dest='bisect', default=None,
        help='Bisect the test suite to discover a test that causes a test '
             'failure when combined with the named test.')
    parser.add_option(
        '--pair', action='store', dest='pair', default=None,
        help='Run the test suite in pairs with the named test to find problem '
             'pairs.')

    options, args = parser.parse_args()
    if options.settings:
        os.environ['DJANGO_SETTINGS_MODULE'] = options.settings
    else:
        if 'DJANGO_SETTINGS_MODULE' not in os.environ:
            os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
        options.settings = os.environ['DJANGO_SETTINGS_MODULE']

    if options.bisect:
        bisect_tests(options.bisect, options, args)
    elif options.pair:
        paired_tests(options.pair, options, args)
    else:
        num_failures = run_tests(int(options.verbosity),
                                 options.interactive,
                                 options.failfast, args)
        if num_failures > 0:
            sys.exit(True)

