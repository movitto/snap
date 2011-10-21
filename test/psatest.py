#!/usr/bin/python
#
# test/psatest.py unit test suite for snap.packagesystemadaptor.PackageSystemAdaptor
#
# (C) Copyright 2011 Mo Morsi (mo@morsi.org)
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License, Version 3,
# as published by the Free Software Foundation
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

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
