# -*- coding:utf-8 -*-

from __future__ import unicode_literals

import codecs
from lxml import etree
import platform
from time import time

from django.utils import six
from django.utils import timezone

from yepes.test.plugins import Plugin
from yepes.test.utils import (
    format_class_name,
    format_exception_message,
    format_exception_name,
    format_traceback,
)


class Xunit(Plugin):
    """
    This plugin provides test results in the standard `XUnit XML format
    <http://help.catchsoftware.com/display/ET/JUnit+Format>`_.

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

    And there is the complete schema in `Relax NG Compact Syntax
    <http://www.relaxng.org/>`_::

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
    def addError(self, test, err):
        """
        Adds error output to Xunit report.
        """
        self.errorCount += 1
        testcase = etree.Element('testcase', attrib={
            'classname': format_class_name(test.__class__),
            'name': test._testMethodName,
            'time': '{0:.3f}'.format(time() - self.testStartTime),
        })
        result = etree.SubElement(testcase, 'error', attrib={
            'type': format_exception_name(err),
            'message': format_exception_message(err),
        })
        result.text = etree.CDATA(format_traceback(err))
        self.results.append(testcase)

    def addExpectedFailure(self, test, err):
        self.addFailure(test, err)

    def addFailure(self, test, err):
        """
        Adds failure output to Xunit report.
        """
        self.failureCount += 1
        testcase = etree.Element('testcase', attrib={
            'classname': format_class_name(test.__class__),
            'name': test._testMethodName,
            'time': '{0:.3f}'.format(time() - self.testStartTime),
        })
        result = etree.SubElement(testcase, 'failure', attrib={
            'type': format_exception_name(err),
            'message': format_exception_message(err),
        })
        result.text = etree.CDATA(format_traceback(err))
        self.results.append(testcase)

    def addSkip(self, test, reason):
        """
        Adds skip output to Xunit report.
        """
        self.skippedCount += 1
        testcase = etree.Element('testcase', attrib={
            'classname': format_class_name(test.__class__),
            'name': test._testMethodName,
            'time': '{0:.3f}'.format(time() - self.testStartTime),
        })
        result = etree.SubElement(testcase, 'skipped')
        self.results.append(testcase)

    def addSuccess(self, test):
        """
        Adds success output to Xunit report.
        """
        self.successCount += 1
        testcase = etree.Element('testcase', attrib={
            'classname': format_class_name(test.__class__),
            'name': test._testMethodName,
            'time': '{0:.3f}'.format(time() - self.testStartTime),
        })
        self.results.append(testcase)

    def addUnexpectedSuccess(self, test):
        self.addSuccess(test)

    def configure(self, options, stream):
        """
        Configures the xunit plugin.
        """
        Plugin.configure(self, options, stream)
        if self.enabled:
            self.fileName = options.xunit_file
            self.mute = int(options.verbosity) < 1

    def options(self, parser):
        """
        Sets additional command line options.
        """
        Plugin.options(self, parser)
        parser.add_option(
            '--xunit-file',
            action='store',
            default='testresults.xml',
            dest='xunit_file',
            help='Path to xml file to store the xunit report in. Default is'
                 ' testresults.xml in the working directory.',
        )

    def report(self):
        """
        Writes an Xunit-formatted XML file.

        This file includes a report of test errors and failures.

        """
        if not self.mute:
            msg = "Writing an XML report of test results in '{0}'..."
            self.stream.writeln(msg.format(self.fileName))
        output_file = codecs.open(self.fileName, 'w', 'UTF-8', 'replace')
        self.writeResults(output_file)
        output_file.close()

    def startTest(self, test):
        """
        Initializes a timer before starting a test.
        """
        self.testStartTime = time()

    def startTestRun(self):
        """
        Initializes some counters and timers before any test is run.
        """
        self.testsRun = 0
        self.errorCount = 0
        self.failureCount = 0
        self.skippedCount = 0
        self.successCount = 0
        self.results = []
        self.startTime = time()
        self.startDateTime = timezone.now()

    def writeResults(self, outputfile):
        """
        Writes an Xunit-formatted XML report in the given file.
        """
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

