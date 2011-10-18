#!/usr/bin/python
#
# test/run.py load unit test suits and run them
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

import sys
sys.path.append("../snap/")

import snap
from callback import TestSystemCallback
snap.callback.snapcallback = TestSystemCallback()

import snaptest
import psatest
import configtest
import recordfilestest

if __name__ == '__main__':
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(snaptest.SnapBaseTest))
    suite.addTest(unittest.makeSuite(psatest.PackageSystemAdaptorTest))
    suite.addTest(unittest.makeSuite(configtest.ConfigManagerTest))
    suite.addTest(unittest.makeSuite(recordfilestest.RecordFilesTest))
    unittest.TextTestRunner(verbosity=2).run(suite)

