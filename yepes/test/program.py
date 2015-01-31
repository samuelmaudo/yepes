# -*- coding:utf-8 -*-

from __future__ import unicode_literals

import fnmatch
import itertools
import logging
import optparse
import os
import shutil
import sys

from unittest.runner import _WritelnDecorator as WriteLnDecorator

from django.utils import six


class TestProgram(object):

    def __init__(self, workingDir, tempDir, templatesDir, subdirsToSkip,
                 alwaysInstalledApps, stream=None):
        self.alwaysInstalledApps = alwaysInstalledApps
        self.plugins = self.loadPlugins()
        self.stream = stream
        self.subdirsToSkip = subdirsToSkip
        self.tempDir = tempDir
        self.templatesDir = templatesDir
        self.workingDir = workingDir

    def configurePlugins(self, options, stream):
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
                configure(options, stream)

    def getTestDiscover(self):
        from yepes.test.discover import TestDiscover
        return TestDiscover

    def getTestModules(self):
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
        return modules

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
        parser = optparse.OptionParser(usage=usage)
        self.options(parser)
        for plugin in self.plugins:
            try:
                addOptions = getattr(plugin, 'addOptions')
            except AttributeError:
                continue
            else:
                addOptions(parser)

        return parser

    def options(self, parser):
        parser.add_option(
            '-v', '--verbosity', action='store', dest='verbosity', default='1',
            type='choice', choices=['0', '1', '2', '3'],
            help='Verbosity level: 0=minimal output, 1=normal output, 2=all '
                 'output')
        parser.add_option(
            '-e', '--exclude', action='append', dest='exclude',
            help='Exclude tests whose label matches the given pattern.')
        parser.add_option(
            '--noinput', action='store_false', dest='interactive', default=True,
            help='Whether NOT prompt the user for input of any kind.')
        parser.add_option(
            '--failfast', action='store_true', dest='failfast', default=False,
            help='Whether stop running the test suite after first failed test.')
        parser.add_option(
            '--settings',
            help='Python path to settings module, e.g. "myproject.settings". If '
                 'this isn\'t provided, the DJANGO_SETTINGS_MODULE environment '
                 'variable will be used.')

    def parseArgs(self, parser):
        options, testLabels = parser.parse_args()
        if options.settings:
            os.environ['DJANGO_SETTINGS_MODULE'] = options.settings
        else:
            if 'DJANGO_SETTINGS_MODULE' not in os.environ:
                os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

            options.settings = os.environ['DJANGO_SETTINGS_MODULE']

        os.environ['DJANGO_TEST_TEMP_DIR'] = self.tempDir

        return (options, testLabels)

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
            print('Failed to remove temp directory: {0}'.format(self.tempDir))

    def restoreSettings(self, settings, old_state):
        """
        Restores the settings to its old state.
        """
        for key, value in six.iteritems(old_state):
            setattr(settings, key, value)

    def run(self):
        parser = self.makeParser()
        options, testLabels = self.parseArgs(parser)
        stream = WriteLnDecorator(self.stream or sys.stderr)
        self.configurePlugins(options, stream)
        return self.runTests(options, testLabels)

    def runTests(self, options, testLabels):
        from django.conf import settings

        verbosity = int(options.verbosity)
        availableTestLabels = self.getTestModules()

        excludedTestLabels = set()
        if options.exclude:
            for pattern in options.exclude:
                excludedTestLabels.update(
                    fnmatch.filter(availableTestLabels, pattern))
                
        if not testLabels:
            finalTestLabels = [
                label
                for label
                in availableTestLabels
                if label not in excludedTestLabels
            ]
        else:
            finalTestLabels = list()
            for pattern in testLabels:
                if '.' not in pattern:
                    finalTestLabels.extend(
                        label
                        for label
                        in fnmatch.filter(availableTestLabels, pattern)
                        if label not in excludedTestLabels
                    )
                else:
                    pattern, path = pattern.split('.', 1)
                    for label in fnmatch.filter(availableTestLabels, pattern):
                        if label not in excludedTestLabels:
                            finalTestLabels.append('.'.join((label, path)))

        state = self.setup(verbosity, finalTestLabels)

        TestDiscover = self.getTestDiscover()
        discover = TestDiscover(
            verbosity=verbosity,
            interactive=options.interactive,
            failfast=options.failfast,
            plugins=self.plugins,
        )
        failureCount = discover.run_tests(finalTestLabels)

        self.teardown(state)
        return failureCount

    def prepareSettings(self, settings):
        """
        Overwrites some settings for the duration of these tests.
        """
        state = {
            'INSTALLED_APPS': settings.INSTALLED_APPS,
            'ROOT_URLCONF': getattr(settings, 'ROOT_URLCONF', ''),
            'TEMPLATE_DIRS': settings.TEMPLATE_DIRS,
            'LANGUAGE_CODE': settings.LANGUAGE_CODE,
            'STATIC_URL': settings.STATIC_URL,
            'STATIC_ROOT': settings.STATIC_ROOT,
        }
        settings.INSTALLED_APPS = self.alwaysInstalledApps
        settings.ROOT_URLCONF = 'urls'
        settings.STATIC_URL = '/static/'
        settings.STATIC_ROOT = os.path.join(self.tempDir, 'static')
        settings.TEMPLATE_DIRS = (os.path.join(self.workingDir, self.templatesDir), )
        settings.LANGUAGE_CODE = 'en'
        settings.SITE_ID = 1
        return state

    def setup(self, verbosity, testLabels):
        from django.conf import settings
        from django.db.models.loading import get_apps, load_app
        from django.test.testcases import TransactionTestCase, TestCase

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
        get_apps()

        # Load all the test model apps.
        testModules = self.getTestModules()

        # Reduce given test labels to just the app module path
        testLabelsSet = set('.'.join(l.split('.')[:1]) for l in testLabels)

        # If the module (or an ancestor) was named on the command line,
        # or no modules were named (i.e., run all), import this module
        # and add it to INSTALLED_APPS.
        def foundInLabels(moduleLabel):
            return any((moduleLabel == label # Exact match
                        or moduleLabel.startswith(label + '.')) # Ancestor match
                    for label
                    in testLabelsSet)

        for moduleLabel in testModules:
            if not testLabels or foundInLabels(moduleLabel):
                if verbosity >= 2:
                    print('Importing application {0}'.format(moduleLabel))
                module = load_app(moduleLabel)
                if module and moduleLabel not in settings.INSTALLED_APPS:
                    settings.INSTALLED_APPS.append(moduleLabel)

        return state

    def teardown(self, state):
        from django.conf import settings
        self.removeTempDir()
        self.restoreSettings(settings, state)

