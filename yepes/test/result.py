# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from unittest import TestResult as BaseTestResult


class TestResult(BaseTestResult):
    """
    A test result class that can print formatted text results to a stream.

    Used by ``SugarTestRunner``.

    """
    def __init__(self, stream, descriptions=None, verbosity=None, plugins=()):
        super(TestResult, self).__init__(stream, descriptions, verbosity)
        self.plugins = plugins

    def addError(self, test, err):
        super(TestResult, self).addError(test, err)
        for plugin in self.plugins:
            try:
                addError = getattr(plugin, 'addError')
            except AttributeError:
                continue
            else:
                addError(test, err)

    def addExpectedFailure(self, test, err):
        super(TestResult, self).addExpectedFailure(test, err)
        for plugin in self.plugins:
            try:
                addExpectedFailure = getattr(plugin, 'addExpectedFailure')
            except AttributeError:
                continue
            else:
                addExpectedFailure(test, err)

    def addFailure(self, test, err):
        super(TestResult, self).addFailure(test, err)
        for plugin in self.plugins:
            try:
                addFailure = getattr(plugin, 'addFailure')
            except AttributeError:
                continue
            else:
                addFailure(test, err)

    def addSkip(self, test, reason):
        super(TestResult, self).addSkip(test, reason)
        for plugin in self.plugins:
            try:
                addSkip = getattr(plugin, 'addSkip')
            except AttributeError:
                continue
            else:
                addSkip(test, reason)

    def addSuccess(self, test):
        super(TestResult, self).addSuccess(test)
        for plugin in self.plugins:
            try:
                addSuccess = getattr(plugin, 'addSuccess')
            except AttributeError:
                continue
            else:
                addSuccess(test)

    def addUnexpectedSuccess(self, test):
        super(TestResult, self).addUnexpectedSuccess(test)
        for plugin in self.plugins:
            try:
                addUnexpectedSuccess = getattr(plugin, 'addUnexpectedSuccess')
            except AttributeError:
                continue
            else:
                addUnexpectedSuccess(test)

    def report(self):
        for plugin in self.plugins:
            try:
                report = getattr(plugin, 'report')
            except AttributeError:
                continue
            else:
                report()

    def startTest(self, test):
        super(TestResult, self).startTest(test)
        for plugin in self.plugins:
            try:
                startTest = getattr(plugin, 'startTest')
            except AttributeError:
                continue
            else:
                startTest(test)

    def startTestRun(self):
        super(TestResult, self).startTestRun()
        for plugin in self.plugins:
            try:
                startTestRun = getattr(plugin, 'startTestRun')
            except AttributeError:
                continue
            else:
                startTestRun()

    def stopTest(self, test):
        super(TestResult, self).startTest(test)
        for plugin in self.plugins:
            try:
                stopTest = getattr(plugin, 'stopTest')
            except AttributeError:
                continue
            else:
                stopTest(test)

    def stopTestRun(self):
        super(TestResult, self).stopTestRun()
        for plugin in self.plugins:
            try:
                stopTestRun = getattr(plugin, 'stopTestRun')
            except AttributeError:
                continue
            else:
                stopTestRun()

