# -*- coding:utf-8 -*-

from __future__ import unicode_literals

import sys

from unittest.runner import _WritelnDecorator as WriteLnDecorator
from unittest.signals import registerResult

from yepes.test.result import TestResult


class TestRunner(object):
    """
    A test result class that can print formatted text results to a stream.

    Used by ``SugarTestRunner``.

    """
    resultclass = TestResult

    def __init__(self, stream=None, verbosity=1, failfast=False,
                 resultclass=None, plugins=()):
        self.stream = WriteLnDecorator(stream or sys.stderr)
        self.verbosity = verbosity
        self.failfast = failfast
        if resultclass is not None:
            self.resultclass = resultclass
        self.plugins = plugins

    def makeResult(self):
        return self.resultclass(
            stream=self.stream,
            verbosity=self.verbosity,
            plugins=[p for p in self.plugins if p.enabled],
        )

    def run(self, test):
        """
        Run the given test case or test suite.
        """
        result = self.makeResult()
        registerResult(result)
        result.failfast = self.failfast

        result.startTestRun()
        try:
            test(result)
        finally:
            result.stopTestRun()

        result.report()
        return result

