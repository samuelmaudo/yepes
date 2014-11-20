# -*- coding:utf-8 -*-

from __future__ import unicode_literals

import codecs
from lxml import etree
import platform
from time import time
import traceback

from django.utils import six
from django.utils import timezone
from django.utils.encoding import force_text

from yepes.test.sugar import (
    SugarDiscoverRunner,
    SugarTestResult,
    SugarTestRunner,
)


class XunitTestResult(SugarTestResult):
    """
    A test result class that write tests results in standard XUnit XML format.

    Used by ``XunitTestRunner``.

    """
    def addError(self, test, err):
        super(XunitTestResult, self).addError(test, err)
        exctype, excvalue, tb = err
        self.errorCount += 1
        testcase = etree.Element('testcase', attrib={
            'classname': '.'.join((
                test.__class__.__module__,
                test.__class__.__name__,
            )),
            'name': test._testMethodName,
            'time': '{0:.3f}'.format(time() - self.testStartTime),
        })
        result = etree.SubElement(testcase, 'error', attrib={
            'type': exctype.__name__,
            'message': force_text(excvalue),
        })
        result.text = etree.CDATA(self.formatException(err))
        self.results.append(testcase)

    def addExpectedFailure(self, test, err):
        self.addSuccess(self, test)

    def addFailure(self, test, err):
        super(XunitTestResult, self).addFailure(test, err)
        exctype, excvalue, tb = err
        self.failureCount += 1
        testcase = etree.Element('testcase', attrib={
            'classname': '.'.join((
                test.__class__.__module__,
                test.__class__.__name__,
            )),
            'name': test._testMethodName,
            'time': '{0:.3f}'.format(time() - self.testStartTime),
        })
        result = etree.SubElement(testcase, 'failure', attrib={
            'type': exctype.__name__,
            'message': force_text(excvalue),
        })
        result.text = etree.CDATA(self.formatException(err))
        self.results.append(testcase)

    def addSkip(self, test, reason):
        super(XunitTestResult, self).addSkip(test, reason)
        self.skippedCount += 1
        testcase = etree.Element('testcase', attrib={
            'classname': '.'.join((
                test.__class__.__module__,
                test.__class__.__name__,
            )),
            'name': test._testMethodName,
            'time': '{0:.3f}'.format(time() - self.testStartTime),
        })
        result = etree.SubElement(testcase, 'skipped')
        self.results.append(testcase)

    def addSuccess(self, test):
        super(XunitTestResult, self).addSuccess(test)
        self.successCount += 1
        testcase = etree.Element('testcase', attrib={
            'classname': '.'.join((
                test.__class__.__module__,
                test.__class__.__name__,
            )),
            'name': test._testMethodName,
            'time': '{0:.3f}'.format(time() - self.testStartTime),
        })
        self.results.append(testcase)

    def addUnexpectedSuccess(self, test):
        self.addSuccess(self, test)

    def formatException(self, exc_info, encoding='utf-8'):
        ec, ev, tb = exc_info

        # Skip test runner traceback levels
        while tb and self._is_relevant_tb_level(tb):
            tb = tb.tb_next

        # Our exception object may have been turned into a string, and Python
        # 3's traceback.format_exception() doesn't take kindly to that (it
        # expects an actual exception object). So we work around it, by doing
        # the work ourselves if ev is not an exception object.
        if isinstance(ev, BaseException):
            return force_text(
                ''.join(traceback.format_exception(ec, ev, tb)),
                encoding,
            )
        else:
            tb_data = force_text(
                ''.join(traceback.format_tb(tb)),
                encoding,
            )
            if not isinstance(ev, six.text_format):
                ev = force_text(repr(ev))

            return tb_data + ev

    def startTest(self, test):
        super(XunitTestResult, self).startTest(test)
        self.testStartTime = time()

    def startTestRun(self):
        super(XunitTestResult, self).startTestRun()
        self.testsRun = 0
        self.errorCount = 0
        self.failureCount = 0
        self.successCount = 0
        self.skippedCount = 0
        self.startTime = time()
        self.startDateTime = timezone.now()
        self.results = []

    def writeResults(self, outputfile):
        timestamp = self.startDateTime.isoformat()
        if self.startDateTime.microsecond:
            timestamp = timestamp[:19] + timestamp[26:]
        if timestamp.endswith('+00:00'):
            timestamp = timestamp[:-6] + 'Z'

        testsuite = etree.Element('testsuite', attrib={
            'name': '.'.join((
                self.__class__.__module__,
                self.__class__.__name__,
            )),
            'tests': six.text_type(self.testsRun),
            'errors': six.text_type(self.errorCount),
            'failures': six.text_type(self.failureCount),
            'skipped': six.text_type(self.skippedCount),
            'time': '{0:.3f}'.format(time() - self.startTime),
            'timestamp': timestamp,
        })
        properties = etree.SubElement(testsuite, 'properties')
        properties.extend([
            etree.Element('property', attrib={
                'name': 'os.name',
                'value': platform.system(),
            }),
            etree.Element('property', attrib={
                'name': 'os.version',
                'value': platform.release(),
            }),
            etree.Element('property', attrib={
                'name': 'os.arch',
                'value': platform.machine(),
            }),
            etree.Element('property', attrib={
                'name': 'python.implementation',
                'value': platform.python_implementation(),
            }),
            etree.Element('property', attrib={
                'name': 'python.version',
                'value': platform.python_version(),
            }),
            etree.Element('property', attrib={
                'name': 'file.encoding',
                'value': 'UTF-8',
            }),
        ])
        testsuite.extend(self.results)
        outputfile.write(etree.tostring(
            testsuite,
            encoding='UTF-8',
            pretty_print=True,
            xml_declaration=True,
        ))


class XunitTestRunner(SugarTestRunner):
    """
    A test runner class that write tests results in standard XUnit XML format.

    There is an abbreviated version of what an XML test report might look like::

        <?xml version="1.0" encoding="UTF-8"?>
        <testsuite name="unittest" tests="1" errors="1" failures="0" skipped="0"
                   time="3.012" timestamp="1986-09-25T12:00:00Z">
            <properties>
                <property name="os.name" value="Linux"/>
                <property name="os.version" value="3.9.1-2-desktop"/>
                <property name="os.arch" value="i686"/>
                <property name="python.implementation" value="CPython"/>
                <property name="python.version" value="2.7.5"/>
                <property name="file.encoding" value="UTF-8"/>
            </properties>
            <testcase classname="path_to_test_suite.TestSomething"
                      name="test_it" time="0.009">
                <error type="exceptions.TypeError" message="oops, wrong type">
                    Traceback (most recent call last):
                    ...
                    TypeError: oops, wrong type
                </error>
            </testcase>
        </testsuite>

    And there is the complete schema in Relax NG Compact Syntax::

        property = element property {
            attribute name {text},
            attribute value {text}
        }

        properties = element properties {
            property*
        }

        error = element error {
            attribute type {text},     # Class name of the exception.
            attribute message {text},  # Message provided by the exception.
            text                       # Traceback.
        }

        failure = element failure {
            attribute type {text},     # Type of assert.
            attribute message {text},  # Message specified in the assert.
            text                       # Traceback.
        }

        skip = element skip { }

        testcase = element testcase {
            attribute classname {text},  # Full name of the class that contains the test method.
            attribute name {text},       # Name of the test method.
            attribute time {text},       # Time taken (in seconds) to run the test.
            (error     # If appear, means that the test is errored.
            |failure,  # If appear, means that the test is failed.
            |skip)?    # If appear, means that the test is skipped.
        }

        testsuite = element testsuite {
            attribute name {text},               # Full class name of the test result.
            attribute tests {xsd:integer},       # Total number of tests in the suite.
            attribute errors {xsd:integer},      # Total number of errored tests in the suite.
            attribute failures {xsd:integer},    # Total number of failed tests in the suite.
            attribute skipped {xsd:integer},     # Total number of skipped tests in the suite.
            attribute time {xsd:double},         # Time taken (in seconds) the run the entire test suite.
            attribute timestamp {xsd:dateTime},  # When the test suite is runned in ISO 8601 format.
            properties?,
            testcase*
        }

    """
    resultclass = XunitTestResult

    def __init__(self, *args, **kwargs):
        self.outputfile = kwargs.pop('outputfile') or 'testresults.xml'
        super(XunitTestRunner, self).__init__(*args, **kwargs)

    def run(self, test):
        result = super(XunitTestRunner, self).run(test)
        self.stream.writeln("Writing test results in '{0}'...".format(
                            self.outputfile))
        outputfile = codecs.open(self.outputfile, 'w', 'UTF-8', 'replace')
        result.writeResults(outputfile)
        outputfile.close()
        return result


class XunitDiscoverRunner(SugarDiscoverRunner):
    """
    A Django test runner that uses unittest2 test discovery and write tests
    results in standard XUnit XML format.
    """

    test_result = XunitTestResult
    test_runner = XunitTestRunner

    def __init__(self, *args, **kwargs):
        self.output_file = kwargs.pop('output_file')
        super(XunitDiscoverRunner, self).__init__(*args, **kwargs)

    def run_suite(self, suite, **kwargs):
        return self.test_runner(
            verbosity=self.verbosity,
            failfast=self.failfast,
            resultclass=self.test_result,
            outputfile=self.output_file,
        ).run(suite)

