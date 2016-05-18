# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from argparse import ArgumentError
import textwrap
from warnings import warn


class Plugin(object):
    """
    Base class for test plugins. It's recommended but not *necessary* to
    subclass this class to create a plugin, but all plugins *must* implement
    `addArguments(self, parser)` and `configure(self, options, stream)`, and
    must have the attributes `enabled` and `name`.  The `name` attribute may
    contain hyphens ('-').

    Plugins should not be enabled by default.

    Subclassing Plugin (and calling the superclass methods in `__init__`,
    `configure`, and `options`, if you override them) will give your plugin
    some friendly default behavior:

    * A --with-$name option will be added to the command line interface to
      enable the plugin, and a corresponding environment variable will be used
      as the default value. The plugin class's docstring will be used as the
      help for this option.

    * The plugin will not be enabled unless this option is selected by the user.

    """
    canConfigure = False
    enabled = False
    enableOpt = None
    name = None

    def __init__(self):
        if self.name is None:
            self.name = self.__class__.__name__.lower()
        if self.enableOpt is None:
            self.enableOpt = 'enable_plugin_{0}'.format(
                              self.name.replace('-', '_'))

    def addArguments(self, parser):
        """
        Add command-line options for this plugin.

        The base plugin class adds --with-$name by default, used to enable the
        plugin.

        .. warning :: Don't implement `addArguments` unless you want to override
                      all default option handling behavior, including warnings
                      for conflicting options. Implement :meth:`options
                      <yepes.test.plugins.base.PluginInterface.options>`
                      instead.

        """
        try:
            self.arguments(parser)
        except ArgumentError as e:
            msg = ("Plugin '{0}' has conflicting option string: '{1}'"
                   " and will be disabled")
            warn(msg.format(self.name, e.option_id), RuntimeWarning)
            self.enabled = False
            self.canConfigure = False
        else:
            self.canConfigure = True

    def arguments(self, parser):
        """
        Register commandline options.

        Implement this method for normal options behavior with protection from
        ArgumentErrors. If you override this method and want the default
        --with-$name option to be registered, be sure to call super().

        """
        parser.add_argument(
            '--with-{0}'.format(self.name),
            action='store_true',
            dest=self.enableOpt,
            default=False,
            help="Enables plugin '{0}'. {1}".format(
                self.name,
                self.help(),
            ),
        )

    def configure(self, options, stream):
        """
        Configure the plugin and system, based on selected options.

        The base plugin class sets the plugin to enabled if the enable option
        for the plugin (self.enableOpt) is true.

        """
        if self.canConfigure:
            self.enabled = getattr(options, self.enableOpt, self.enabled)
            self.stream = stream

    def help(self):
        """
        Return help for this plugin. This will be output as the help
        section of the --with-$name option that enables the plugin.
        """
        docs = self.__class__.__doc__
        if docs:
            # doc sections are often indented; compress the spaces
            return textwrap.dedent(docs.splitlines()[0])
        else:
            return '(no help available)'


class PluginInterface(object):
    """
    PluginInterface describes the plugin API. Do not subclass or use this class
    directly.
    """
    def __new__(cls, *arg, **kw):
        raise TypeError('PluginInterface class is for documentation only')

    def addArguments(self, parser):
        """
        Called to allow plugin to register command-line options with the parser.

        .. warning :: Don't implement `addArguments` unless you want to override
                      all default option handling behavior, including warnings
                      for conflicting options. Implement :meth:`options
                      <yepes.test.plugins.base.PluginInterface.options>`
                      instead.

        """
        pass

    def addError(self, test, err):
        """
        Called when a test raises an uncaught exception.

        :param test:    The test case that was errored.
        :type test:     :class:`unittest.case.TestCase`
        :param err:     A tuple of the form returned by :func:`sys.exc_info`:
                        ``(type, value, traceback)``.
        :type err:      tuple

        """
        pass

    def addExpectedFailure(self, test, err):
        """
        Called when the test case test fails, but was marked with the
        :func:`unittest.case.expectedFailure()` decorator.

        :param test:    The test case that was failed (as was expected).
        :type test:     :class:`unittest.case.TestCase`
        :param err:     A tuple of the form returned by :func:`sys.exc_info`:
                        ``(type, value, traceback)``.
        :type err:      tuple

        """
        pass

    def addFailure(self, test, err):
        """
        Called when a test fails.

        :param test:    The test case that was failed.
        :type test:     :class:`unittest.case.TestCase`
        :param err:     A tuple of the form returned by :func:`sys.exc_info`:
                        ``(type, value, traceback)``.
        :type err:      tuple

        """
        pass

    def addSkip(self, test, reason):
        """
        Called when a test is skipped.

        :param test:    The test case that was skipped.
        :type test:     :class:`unittest.case.TestCase`
        :param reason:  The reason for skipping the test.
        :type reason:   str

        """
        pass

    def addSuccess(self, test):
        """
        Called when a test passes.

        :param test:    The test case that was successful.
        :type test:     :class:`unittest.case.TestCase`

        """
        pass

    def addUnexpectedSuccess(self, test):
        """
        Called when the test case test was marked with the
        :func:`unittest.case.expectedFailure` decorator, but succeeded.

        :param test:    The test case that was surprisingly successful.
        :type test:     :class:`unittest.case.TestCase`

        """
        pass

    def configure(self, options, stream):
        """
        Called after the command line has been parsed, with the parsed options
        and the output stream. Here, implement any config storage or changes
        to state or operation that are set by command line options.

        :param options: An object that stores all plugin options.
        :type options:  :class:`argparse.Values`
        :param stream:  Stream object, send your output here.
        :type stream:   file-like object

        """
        pass

    def arguments(self, parser):
        """
        Called to allow plugin to register command line options with the parser.

        :param parser:  Options parser instance.
        :type parser:   :class:`argparse.OptionParser`

        """
        pass

    def report(self):
        """
        Called after all tests are run. Use this to print your plugin's report.
        """
        pass

    def startTest(self, test):
        """
        Called before each test is run.

        :param test:    The test case.
        :type test:     :class:`unittest.case.TestCase`

        """
        pass

    def startTestRun(self):
        """
        Called before any tests are run. Use this to perform any setup needed
        before testing begins.
        """
        pass

    def stopTest(self, test):
        """
        Called after each test is run.

        :param test:    The test case.
        :type test:     :class:`unittest.case.TestCase`

        """
        pass

    def stopTestRun(self):
        """
        Called after all tests are run. Use this to perform final cleanup.
        """
        pass

