# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from time import time

from yepes.test.plugins.base import Plugin
from yepes.test.utils import format_traceback

TERMINAL_COLORS = {
    'error': '\033[1;91m',    # Bold, Light red
    'gray': '\033[90m',       # Dark gray
    'reset': '\033[0m',       # Reset all attributes
    'success': '\033[92m',    # Light green
    'warning': '\033[1;93m',  # Bold, Light yellow
}


class Sugar(Plugin):
    """
    This plugin provides pretty text results to the output stream.

    It outputs the names of tests as they are run, errors as they
    occur, and a summary of the results at the end of the test run.

    Their look an feel is inspired on `pytest-sugar`.

    """
    dictionary = {
        'error': TERMINAL_COLORS['error'] + 'ERROR' + TERMINAL_COLORS['reset'],
        'error_abbr': TERMINAL_COLORS['error'] + 'x' + TERMINAL_COLORS['reset'],
        'expected_failure': TERMINAL_COLORS['success'] + 'expected failure' + TERMINAL_COLORS['reset'],
        'expected_failure_abbr': TERMINAL_COLORS['success'] + 'x' + TERMINAL_COLORS['reset'],
        'failure': TERMINAL_COLORS['error'] + 'FAIL' + TERMINAL_COLORS['reset'],
        'failure_abbr': TERMINAL_COLORS['error'] + 'x' + TERMINAL_COLORS['reset'],
        'skip': TERMINAL_COLORS['success'] + 'skipped {0!r}' + TERMINAL_COLORS['reset'],
        'skip_abbr': TERMINAL_COLORS['success'] + 's' + TERMINAL_COLORS['reset'],
        'success': TERMINAL_COLORS['success'] + 'ok' + TERMINAL_COLORS['reset'],
        'success_abbr': TERMINAL_COLORS['success'] + '.' + TERMINAL_COLORS['reset'],
        'unexpected_success': TERMINAL_COLORS['warning'] + 'unexpected success' + TERMINAL_COLORS['reset'],
        'unexpected_success_abbr': TERMINAL_COLORS['warning'] + '.' + TERMINAL_COLORS['reset'],
    }
    separator1 = '=' * 70
    separator2 = '-' * 70

    def addError(self, test, err):
        self.errors.append((test, err))
        if self.showAll:
            self.stream.writeln(self.dictionary['error'])
        elif not self.mute:
            self.stream.write(self.dictionary['error_abbr'])
            self.stream.flush()

    def addExpectedFailure(self, test, err):
        self.expectedFailures.append((test, err))
        if self.showAll:
            self.stream.writeln(self.dictionary['expected_failure'])
        elif not self.mute:
            self.stream.write(self.dictionary['expected_failure_abbr'])
            self.stream.flush()

    def addFailure(self, test, err):
        self.failures.append((test, err))
        if self.showAll:
            self.stream.writeln(self.dictionary['failure'])
        elif not self.mute:
            self.stream.write(self.dictionary['failure_abbr'])
            self.stream.flush()

    def addSkip(self, test, reason):
        self.errors.append((test, reason))
        if self.showAll:
            self.stream.writeln(self.dictionary['skip'].format(reason))
        elif not self.mute:
            self.stream.write(self.dictionary['skip_abbr'])
            self.stream.flush()

    def addSuccess(self, test):
        if self.showAll:
            self.stream.writeln(self.dictionary['success'])
        elif not self.mute:
            self.stream.write(self.dictionary['success_abbr'])
            self.stream.flush()

    def addUnexpectedSuccess(self, test):
        self.unexpectedSuccesses.append(test)
        if self.showAll:
            self.stream.writeln(self.dictionary['unexpected_success'])
        elif not self.mute:
            self.stream.write(self.dictionary['unexpected_success_abbr'])
            self.stream.flush()

    def arguments(self, parser):
        """
        Add command-line options for this plugin.
        """
        parser.add_argument(
            '--without-sugar',
            action='store_false',
            dest=self.enableOpt,
            default=True,
            help="Disables plugin '{0}'. {1}".format(
                self.name,
                self.help(),
            ),
        )

    def configure(self, options, stream):
        """
        Configures the sugar plugin.
        """
        Plugin.configure(self, options, stream)
        if self.enabled:
            self.mute = int(options.verbosity) < 1
            self.showAll = int(options.verbosity) > 1
            self.testsRun = 0
            self.failures = []
            self.errors = []
            self.expectedFailures = []
            self.skipped = []
            self.unexpectedSuccesses = []
            self.lastTestCase = None

    def getAbbreviatedDescription(self, test):
        try:
            test._testMethodName
        except AttributeError:
            # This handles class or module level exceptions.
            i = test.description.index('(') + 1
            j = test.description.index(')')
            full_name = test.description[i:j]
            if '.' in full_name:
                module, name = full_name.rsplit('.', 1)
            else:
                module = None
                name = full_name
        else:
            module = test.__class__.__module__
            name = test.__class__.__name__

        if not module:
            return name
        else:
            return ''.join((
                TERMINAL_COLORS['gray'],
                module,
                '.',
                TERMINAL_COLORS['reset'],
                name,
            ))

    def getDescription(self, test):
        try:
            method_name = test._testMethodName
        except AttributeError:
            # This handles class or module level exceptions.
            i = test.description.index(' ')
            method_name = test.description[:i]

        return ''.join((
            method_name,
            ' ',
            TERMINAL_COLORS['gray'],
            '(',
            TERMINAL_COLORS['reset'],
            self.getAbbreviatedDescription(test),
            ')',
        ))

    def printErrors(self):
        if not self.mute:
            self.stream.writeln()
        self.printErrorList('ERROR', self.errors)
        self.printErrorList('FAIL', self.failures)

    def printErrorList(self, flavour, errors):
        for test, err in errors:
            self.stream.writeln(self.separator1)
            self.stream.writeln('{0}: {1}'.format(flavour, self.getDescription(test)))
            self.stream.writeln(self.separator2)
            self.stream.writeln(format_traceback(err, 'ascii'))

    def report(self):
        self.printErrors()
        self.stream.writeln(self.separator2)
        self.stream.writeln(
            'Ran {0} test{1} in {2:.3f}s'.format(
                    self.testsRun,
                    's' if self.testsRun != 1 else '',
                    self.stopTime - self.startTime)
        )
        self.stream.writeln()

        infos = []
        if (self.failures or self.errors):
            self.stream.write('FAILED')
            if self.failures:
                infos.append('failures={0}'.format(len(self.failures)))
            if self.errors:
                infos.append('errors={0}'.format(len(self.errors)))
        else:
            self.stream.write('OK')

        if self.skipped:
            infos.append('skipped={0}'.format(len(self.skipped)))
        if self.expectedFailures:
            infos.append('expected failures={0}'.format(len(self.expectedFailures)))
        if self.unexpectedSuccesses:
            infos.append('unexpected successes={0}'.format(len(self.unexpectedSuccesses)))

        if infos:
            self.stream.writeln(' ({0})'.format(', '.join(infos)))

        self.stream.writeln()

    def startTest(self, test):
        self.testsRun += 1
        if self.showAll:
            self.stream.write(self.getDescription(test))
            self.stream.write(' ... ')
            self.stream.flush()
        elif (not self.mute
                and self.lastTestCase is not test.__class__):
            self.lastTestCase = test.__class__
            self.stream.write('\n')
            self.stream.write(self.getAbbreviatedDescription(test))
            self.stream.write(' ')
            self.stream.flush()

    def startTestRun(self):
        self.startTime = time()

    def stopTestRun(self):
        self.stopTime = time()
        if not self.mute:
            self.stream.writeln()

