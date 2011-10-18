#!/usr/bin/python
#
# test/psatest.py unit test suite for snap.packagesystemadaptor.PackageSystemAdaptor
#
# Version: 0.1
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# (C) Copyright 2007 Mohammed Morsi (movitto@yahoo.com)

import unittest

from snap.packages import Package
from snap.exceptions import SnapPackageSystemError
from snap.packagesystemadaptor import SnapPackageSystemAdaptor

class PackageSystemAdaptorTest(unittest.TestCase):
    testplugins = [ 'yum' ]

    def testLoadInvalidPlugin(self):
        psa = SnapPackageSystemAdaptor
        self.assertRaises(SnapPackageSystemError, psa, 'foobar')

    def testInvokeInterface(self):
        for testplugin in self.testplugins:
            psa = SnapPackageSystemAdaptor(testplugin)
            installedpackages = psa.get_installed_packages()
            for installedpkg in installedpackages:
                self.assertEqual(installedpkg.__class__, Package)
            status = psa.get_file_status('/etc/passwd')
            self.assert_(status == True or status == False)
