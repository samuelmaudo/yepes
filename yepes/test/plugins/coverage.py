# -*- coding:utf-8 -*-

from __future__ import absolute_import, unicode_literals

import coverage
import os
import pkgutil

from django.utils import six
from django.utils._os import upath

from yepes.test.plugins.base import Plugin


class Coverage(Plugin):
    """
    This plugin provides coverage reports by using Ned Batchelder's coverage
    module.
    """

    def arguments(self, parser):
        """
        Sets additional command line options.
        """
        Plugin.arguments(self, parser)
        parser.add_argument(
            '--cover-package',
            action='append',
            dest='cover_packages',
            help='Restrict coverage output to selected packages.',
        )
        parser.add_argument(
            '--cover-branches',
            action='store_true',
            default=False,
            dest='cover_branches',
            help='Include branch coverage in coverage report.',
        )
        parser.add_argument(
            '--cover-erase',
            action='store_true',
            default=False,
            dest='cover_erase',
            help='Erase previously collected coverage statistics before run.',
        )
        parser.add_argument(
            '--cover-html',
            action='store_true',
            default=False,
            dest='cover_html',
            help='Produce an HTML report with coverage information.',
        )
        parser.add_argument(
            '--cover-html-dir',
            action='store',
            default='htmlcov',
            dest='cover_html_dir',
            help='Path to dir to store the HTML coverage report. Default is'
                 ' htmlcov in the working directory.',
        )
        parser.add_argument(
            '--cover-xml',
            action='store_true',
            default=False,
            dest='cover_xml',
            help='Produce an XML report with coverage information.',
        )
        parser.add_argument(
            '--cover-xml-file',
            action='store',
            default='coverage.xml',
            dest='cover_xml_file',
            help='Path to file to store the XML coverage report. Default is'
                 ' coverage.xml in the working directory.',
        )

    def configure(self, options, stream):
        """
        Configures the coverage plugin and starts measuring code coverage.
        """
        Plugin.configure(self, options, stream)
        if self.enabled:
            self.mute = int(options.verbosity) < 1
            self.showAll = int(options.verbosity) > 1

            if options.cover_packages:
                packages = []
                for name in options.cover_packages:
                    pkg = pkgutil.get_loader(name)
                    if pkg is None:
                        msg = "Failed to find package '{0}'"
                        raise AttributeError(msg.format(name))

                    if six.PY2:
                        file_name = pkg.filename
                    else:
                        file_name = pkg.name

                    packages.append(os.path.abspath(upath(file_name)))

                self.includedPackages = packages
            else:
                self.includedPackages = None

            self.erasePrevious = options.cover_erase
            self.includeBranches = options.cover_branches
            if options.cover_html:
                self.htmlDirName = options.cover_html_dir
            else:
                self.htmlDirName = None

            if options.cover_xml:
                self.xmlFileName = options.cover_xml_file
            else:
                self.xmlFileName = None

            self.coverageInstance = coverage.coverage(
                branch=self.includeBranches,
                source=self.includedPackages,
            )
            if self.erasePrevious:
                self.coverageInstance.erase()
            else:
                self.coverageInstance.load()

            # Start measuring as soon as posible is necessary
            # to obtain a realistic coverage report.
            self.coverageInstance.start()

    def report(self):
        """
        Outputs coverage reports.
        """
        if self.showAll:
            self.coverageInstance.report(file=self.stream)

        if self.htmlDirName is not None:
            if not self.mute:
                msg = "Writing an HTML report of coverage results in '{0}'..."
                self.stream.writeln(msg.format(self.htmlDirName))
            try:
                self.coverageInstance.html_report(directory=self.htmlDirName)
            except coverage.misc.CoverageException as e:
                msg = 'Failed to generate HTML report: {0}'
                self.stream.writeln(msg.format(e))

        if self.xmlFileName is not None:
            if not self.mute:
                msg = "Writing an XML report of coverage results in '{0}'..."
                self.stream.writeln(msg.format(self.xmlFileName))
            try:
                self.coverageInstance.xml_report(outfile=self.xmlFileName)
            except coverage.misc.CoverageException as e:
                msg = 'Failed to generate XML report: {0}'
                self.stream.writeln(msg.format(e))

    def stopTestRun(self):
        """
        Stops measuring code coverage.
        """
        self.coverageInstance.stop()
        self.coverageInstance.combine()
        self.coverageInstance.save()

