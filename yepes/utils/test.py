# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from functools import wraps
from unittest import TestResult, TextTestRunner

from django.test.runner import DiscoverRunner
from django.utils import six

from yepes.apps.registry import registry

TERMINAL_COLORS = {
    'error': '\033[1;91m',    # Bold, Light red
    'gray': '\033[90m',       # Dark gray
    'reset': '\033[0m',       # Reset all attributes
    'info': '\033[94m',       # Light blue
    'success': '\033[92m',    # Light green
    'warning': '\033[1;93m',  # Bold, Light yellow
}

__all__ = (
    'override_registry',
    'SugarDiscoverRunner', 'SugarTestResult', 'SugarTestRunner',
)


class override_registry(object):
    """
    Acts as either a decorator, or a context manager. If it's a decorator it
    takes a function and returns a wrapped function. If it's a contextmanager
    it's used with the ``with`` statement. In either event entering/exiting
    are called before and after, respectively, the function/block is executed.
    """
    def __init__(self, values):
        self.new_values = values

    def __enter__(self):
        self.enable()

    def __exit__(self, exc_type, exc_value, traceback):
        self.disable()

    def __call__(self, test_func):
        from django.test import SimpleTestCase
        if isinstance(test_func, type):
            if not issubclass(test_func, SimpleTestCase):
                msg = ('Only subclasses of Django SimpleTestCase can be'
                       ' decorated with override_registry')
                raise Exception(msg)

            original_pre_setup = test_func._pre_setup
            original_post_teardown = test_func._post_teardown

            def _pre_setup(innerself):
                self.enable()
                original_pre_setup(innerself)

            def _post_teardown(innerself):
                original_post_teardown(innerself)
                self.disable()

            test_func._pre_setup = _pre_setup
            test_func._post_teardown = _post_teardown
            return test_func
        else:
            @wraps(test_func)
            def inner(*args, **kwargs):
                with self:
                    return test_func(*args, **kwargs)

        return inner

    def enable(self):
        self.old_values = {
            key: registry.get(key)
            for key
            in six.iterkeys(self.new_values)
        }
        for key, value in six.iteritems(self.new_values):
            registry[key] = value

    def disable(self):
        for key, value in six.iteritems(self.old_values):
            registry[key] = value

        del self.old_values


class SugarTestResult(TestResult):
    """
    A test result class that can print formatted text results to a stream.

    Used by ``SugarTestRunner``.

    """
    dictionary = {
        'error': TERMINAL_COLORS['error'] + 'ERROR' + TERMINAL_COLORS['reset'],
        'error_abbr': TERMINAL_COLORS['error'] + '⨯' + TERMINAL_COLORS['reset'],
        'expected_failure': TERMINAL_COLORS['info'] + 'expected failure' + TERMINAL_COLORS['reset'],
        'expected_failure_abbr': TERMINAL_COLORS['info'] + '⨯' + TERMINAL_COLORS['reset'],
        'failure': TERMINAL_COLORS['error'] + 'FAIL' + TERMINAL_COLORS['reset'],
        'failure_abbr': TERMINAL_COLORS['error'] + '⨯' + TERMINAL_COLORS['reset'],
        'skip': TERMINAL_COLORS['info'] + 'skipped {0!r}' + TERMINAL_COLORS['reset'],
        'skip_abbr': TERMINAL_COLORS['info'] + 's' + TERMINAL_COLORS['reset'],
        'success': TERMINAL_COLORS['success'] + 'ok' + TERMINAL_COLORS['reset'],
        'success_abbr': TERMINAL_COLORS['success'] + '✓' + TERMINAL_COLORS['reset'],
        'unexpected_success': TERMINAL_COLORS['warning'] + 'unexpected success' + TERMINAL_COLORS['reset'],
        'unexpected_success_abbr': TERMINAL_COLORS['warning'] + '✓' + TERMINAL_COLORS['reset'],
    }
    separator1 = '=' * 70
    separator2 = '-' * 70

    def __init__(self, stream, descriptions, verbosity):
        super(SugarTestResult, self).__init__(stream, descriptions, verbosity)
        self.stream = stream
        self.showAll = verbosity > 1
        self.dots = verbosity == 1

    def getAbbreviatedDescription(self, test):
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
        return ''.join((
            test._testMethodName,
            ' ',
            TERMINAL_COLORS['gray'],
            '(',
            TERMINAL_COLORS['reset'],
            self.getAbbreviatedDescription(test),
            ')',
        ))

    def addError(self, test, err):
        super(SugarTestResult, self).addError(test, err)
        if self.showAll:
            self.stream.writeln(self.dictionary['error'])
        elif self.dots:
            self.stream.write(self.dictionary['error_abbr'])
            self.stream.flush()

    def addExpectedFailure(self, test, err):
        super(SugarTestResult, self).addExpectedFailure(test, err)
        if self.showAll:
            self.stream.writeln(self.dictionary['expected_failure'])
        elif self.dots:
            self.stream.write(self.dictionary['expected_failure_abbr'])
            self.stream.flush()

    def addFailure(self, test, err):
        super(SugarTestResult, self).addFailure(test, err)
        if self.showAll:
            self.stream.writeln(self.dictionary['failure'])
        elif self.dots:
            self.stream.write(self.dictionary['failure_abbr'])
            self.stream.flush()

    def addSkip(self, test, reason):
        super(SugarTestResult, self).addSkip(test, reason)
        if self.showAll:
            self.stream.writeln(self.dictionary['skip'].format(reason))
        elif self.dots:
            self.stream.write(self.dictionary['skip_abbr'])
            self.stream.flush()

    def addSuccess(self, test):
        super(SugarTestResult, self).addSuccess(test)
        if self.showAll:
            self.stream.writeln(self.dictionary['success'])
        elif self.dots:
            self.stream.write(self.dictionary['success_abbr'])
            self.stream.flush()

    def addUnexpectedSuccess(self, test):
        super(SugarTestResult, self).addUnexpectedSuccess(test)
        if self.showAll:
            self.stream.writeln(self.dictionary['unexpected_success'])
        elif self.dots:
            self.stream.write(self.dictionary['unexpected_success_abbr'])
            self.stream.flush()

    def printErrors(self):
        if self.dots or self.showAll:
            self.stream.writeln()
        self.printErrorList('ERROR', self.errors)
        self.printErrorList('FAIL', self.failures)

    def printErrorList(self, flavour, errors):
        for test, err in errors:
            self.stream.writeln(self.separator1)
            self.stream.writeln('{0}: {1}'.format(flavour, self.getDescription(test)))
            self.stream.writeln(self.separator2)
            self.stream.writeln('{0}'.format(err))

    def startTest(self, test):
        super(SugarTestResult, self).startTest(test)
        if self.showAll:
            self.stream.write(self.getDescription(test))
            self.stream.write(' ... ')
            self.stream.flush()
        elif self.dots:
            test_case = test.__class__
            if self.last_test_case is not test_case:
                self.last_test_case = test_case
                self.stream.write('\n')
                self.stream.write(self.getAbbreviatedDescription(test))
                self.stream.write(' ')
                self.stream.flush()

    def startTestRun(self):
        super(SugarTestResult, self).startTestRun()
        self.last_test_case = None

    def stopTestRun(self):
        super(SugarTestResult, self).stopTestRun()
        if self.dots:
            self.stream.writeln()


class SugarTestRunner(TextTestRunner):
    """
    A test runner class that displays results in textual form.

    It prints out the names of tests as they are run, errors as they
    occur, and a summary of the results at the end of the test run.

    Their look an feel is inspired on ``pytest-sugar``.

    """
    resultclass = SugarTestResult


class SugarDiscoverRunner(DiscoverRunner):
    """
    A Django test runner that uses unittest2 test discovery and has
    a sugary look and feel.
    """

    test_result = SugarTestResult
    test_runner = SugarTestRunner

    def run_suite(self, suite, **kwargs):
        return self.test_runner(
            verbosity=self.verbosity,
            failfast=self.failfast,
            resultclass=self.test_result,
        ).run(suite)
