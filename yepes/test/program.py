# -*- coding:utf-8 -*-

from __future__ import unicode_literals

import fnmatch
import importlib
import logging
import argparse
import os
import shutil
import sys

from unittest.runner import _WritelnDecorator as WriteLnDecorator

import django

from django.apps import AppConfig, apps
from django.conf import settings
from django.test.testcases import TransactionTestCase, TestCase
from django.utils import six


class TestProgram(object):

    def __init__(self, workingDir, tempDir, templatesDir, subdirsToSkip,
                 alwaysInstalledApps, stream=None):
        if stream is None:
            stream = sys.stderr

        if not isinstance(stream, WriteLnDecorator):
            stream = WriteLnDecorator(stream)

        self.alwaysInstalledApps = alwaysInstalledApps
        self.plugins = self.loadPlugins()
        self.stream = stream
        self.subdirsToSkip = subdirsToSkip
        self.tempDir = tempDir
        self.templatesDir = templatesDir
        self.workingDir = workingDir

    def arguments(self, parser):
        parser.add_argument('args', metavar='label', nargs='*')
        parser.add_argument(
            '-v', '--verbosity', action='store', dest='verbosity', default=1,
            type=int, choices=[0, 1, 2, 3],
            help='Verbosity level: 0=minimal output, 1=normal output, 2=all '
                 'output')
        parser.add_argument(
            '-e', '--exclude', action='append', dest='exclude',
            help='Exclude tests whose label matches the given pattern.')
        parser.add_argument(
            '--noinput', action='store_false', dest='interactive', default=True,
            help='Whether NOT prompt the user for input of any kind.')
        parser.add_argument(
            '--failfast', action='store_true', dest='failfast', default=False,
            help='Whether stop running the test suite after first failed test.')
        parser.add_argument(
            '--settings',
            help='Python path to settings module, e.g. "myproject.settings". If '
                 'this isn\'t provided, the DJANGO_SETTINGS_MODULE environment '
                 'variable will be used.')

    def configurePlugins(self, options):
        """
        Configure the plugin and system, based on selected options.

        The base plugin class sets the plugin to enabled if the enable option
        for the plugin (self.enableOpt) is true.

        """
        for plugin in self.plugins:
            try:
                configure = getattr(plugin, 'configure')
            except AttributeError:
                continue
            else:
                configure(options, self.stream)

    def getAvailableTestLabels(self):
        modules = [
            dirName
            for dirName
            in os.listdir(self.workingDir)
            if ('.' not in dirName
                    and dirName != '__pycache__'
                    and not dirName.startswith('sql')
                    and os.path.basename(dirName) not in self.subdirsToSkip
                    and not os.path.isfile(dirName))
        ]
        modules.sort()
        return modules

    def getTestDiscover(self):
        from yepes.test.discover import TestDiscover
        return TestDiscover

    def getTestLabels(self, testLabels, options):
        availableTestLabels = self.getAvailableTestLabels()

        excludedTestLabels = set()
        if options.exclude:
            for pattern in options.exclude:
                foundLabels = fnmatch.filter(availableTestLabels, pattern)
                if not foundLabels:
                    msg = "Failed to find test matching '{0}'"
                    raise AttributeError(msg.format(pattern))

                excludedTestLabels.update(foundLabels)

        if not testLabels:
            finalTestLabels = list(
                label
                for label
                in availableTestLabels
                if label not in excludedTestLabels
            )
        else:
            finalTestLabels = list()
            for pattern in testLabels:
                if '.' in pattern:
                    pattern, path = pattern.split('.', 1)
                else:
                    path = None

                foundLabels = fnmatch.filter(availableTestLabels, pattern)
                if not foundLabels:
                    msg = "Failed to find test matching '{0}'"
                    raise AttributeError(msg.format(pattern))

                finalTestLabels.extend(
                    label if path is None else '.'.join((label, path))
                    for label
                    in foundLabels
                    if label not in excludedTestLabels
                )

        return finalTestLabels

    def loadPlugins(self):
        plugins = []
        try:
            from yepes.test.plugins import sugar
        except ImportError:
            pass
        else:
            plugins.append(sugar.Sugar())
        try:
            from yepes.test.plugins import xunit
        except ImportError:
            pass
        else:
            plugins.append(xunit.Xunit())
        try:
            from yepes.test.plugins import coverage
        except ImportError:
            pass
        else:
            plugins.append(coverage.Coverage())

        return plugins

    def makeParser(self):
        usage = '%prog [options] [module module module ...]'
        parser = argparse.ArgumentParser(usage=usage)
        self.arguments(parser)
        for plugin in self.plugins:
            try:
                addArguments = plugin.addArguments
            except AttributeError:
                continue
            else:
                addArguments(parser)

        return parser

    def parseArgs(self, parser):
        args = parser.parse_args()
        if args.settings:
            os.environ['DJANGO_SETTINGS_MODULE'] = args.settings
        else:
            if 'DJANGO_SETTINGS_MODULE' not in os.environ:
                os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

            args.settings = os.environ['DJANGO_SETTINGS_MODULE']

        os.environ['DJANGO_TEST_TEMP_DIR'] = self.tempDir
        return args

    def removeTempDir(self):
        """
        Removes the temporary directory.
        """
        try:
            # Ensure we pass in unicode so that it will successfully remove
            # temp trees containing non-ASCII filenames on Windows. (We're
            # assuming the temp dir name itself does not contain non-ASCII
            # characters.)
            shutil.rmtree(six.text_type(self.tempDir))
        except OSError:
            msg = 'Failed to remove temp directory: {0}'
            self.stream.writeln(msg.format(self.tempDir))

    def restoreSettings(self, settings, old_state):
        """
        Restores the settings to its old state.
        """
        for key, value in six.iteritems(old_state):
            setattr(settings, key, value)

    def run(self):
        parser = self.makeParser()
        options = self.parseArgs(parser)
        testLabels = options.args
        self.configurePlugins(options)
        return self.runTests(testLabels, options)

    def runTests(self, testLabels, options):
        verbosity = int(options.verbosity)
        finalTestLabels = self.getTestLabels(testLabels, options)
        state = self.setup(verbosity, finalTestLabels)

        TestDiscover = self.getTestDiscover()
        failureCount = TestDiscover(
            verbosity=verbosity,
            interactive=options.interactive,
            failfast=options.failfast,
            plugins=self.plugins,
            stream=self.stream,
        ).run_tests(finalTestLabels)

        self.teardown(state)
        return failureCount

    def prepareSettings(self, settings):
        """
        Overwrites some settings for the duration of these tests.
        """
        state = {
            'INSTALLED_APPS': settings.INSTALLED_APPS,
            'ROOT_URLCONF': getattr(settings, 'ROOT_URLCONF', ''),
            'TEMPLATES': settings.TEMPLATES,
            'LANGUAGE_CODE': settings.LANGUAGE_CODE,
            'STATIC_URL': settings.STATIC_URL,
            'STATIC_ROOT': settings.STATIC_ROOT,
        }
        settings.INSTALLED_APPS = self.alwaysInstalledApps
        settings.ROOT_URLCONF = 'urls'
        settings.STATIC_URL = '/static/'
        settings.STATIC_ROOT = os.path.join(self.tempDir, 'static')
        settings.TEMPLATES = [{
            'BACKEND': 'django.template.backends.django.DjangoTemplates',
            'DIRS': [os.path.join(self.workingDir, self.templatesDir)],
            'APP_DIRS': True,
            'OPTIONS': {
                'context_processors': [
                    'django.template.context_processors.debug',
                    'django.template.context_processors.request',
                    'django.contrib.auth.context_processors.auth',
                    'django.contrib.messages.context_processors.messages',
                ],
            },
        }]
        settings.LANGUAGE_CODE = 'en'
        settings.SITE_ID = 1
        settings.MIGRATION_MODULES = {
            # These 'tests.migrations' modules don't actually exist, but
            # this lets us skip creating migrations for the test models.
            'auth': 'django.contrib.auth.migrations_',
            'contenttypes': 'django.contrib.contenttypes.migrations_',
            'sessions': 'django.contrib.sessions.migrations_',
        }
        return state

    def setup(self, verbosity, testLabels):
        # Force declaring available_apps in TransactionTestCase for faster tests.
        def noAvailableApps(self):
            raise Exception('Please define available_apps in'
                            ' TransactionTestCase and its subclasses.')
        TransactionTestCase.available_apps = property(noAvailableApps)
        TestCase.available_apps = None

        state = self.prepareSettings(settings)

        if verbosity > 0:
            # Ensure any warnings captured to logging are piped through a verbose
            # logging handler. If any -W options were passed explicitly on command
            # line, warnings are not captured, and this has no effect.
            logger = logging.getLogger('py.warnings')
            handler = logging.StreamHandler()
            logger.addHandler(handler)

        # Load all the self.alwaysInstalledApps.
        django.setup()

        # Reduce given test labels to just the app module path
        appNames = set(l.split('.', 1)[0] for l in testLabels)

        # Load all the test model apps.
        if verbosity >= 2:
            self.stream.writeln('Importing applications ...')

        for name in appNames:
            if verbosity >= 2:
                self.stream.writeln('Importing application {0}'.format(name))

            module = importlib.import_module(name)
            config = AppConfig(name, module)
            config.label = '_'.join((config.label.strip('_'), 'tests'))
            settings.INSTALLED_APPS.append(config)

        apps.set_installed_apps(settings.INSTALLED_APPS)

        return state

    def teardown(self, state):
        self.removeTempDir()
        self.restoreSettings(settings, state)

