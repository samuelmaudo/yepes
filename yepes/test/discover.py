# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from django.test.runner import DiscoverRunner

from yepes.test.result import TestResult
from yepes.test.runner import TestRunner


class TestDiscover(DiscoverRunner):
    """
    A test result class that can print formatted text results to a stream.

    Used by ``SugarTestDiscover``.

    """
    test_result = TestResult
    test_runner = TestRunner

    def __init__(self, *args, **kwargs):
        self.stream = kwargs.get('stream')
        self.plugins = kwargs.get('plugins', ())
        super(TestDiscover, self).__init__(*args, **kwargs)

    def run_suite(self, suite, **kwargs):
        return self.test_runner(
            stream=self.stream,
            verbosity=self.verbosity,
            failfast=self.failfast,
            resultclass=self.test_result,
            plugins=self.plugins,
        ).run(suite)
