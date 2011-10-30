#!/usr/bin/python
#
# test/run.py load unit test suits and run them
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

import sys
sys.path.append("../snap/")

import snap
import callback

import configtest
import cryptotest
import filemanagertest
import packagemetadatatest
import servicesmetadatatest
import sfilemetadatatest
import snapfiletest
import snaptest
import yumbackendtest
import servicedispatchertest

if __name__ == '__main__':
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(configtest.ConfigTest))
    suite.addTest(unittest.makeSuite(cryptotest.CryptoTest))
    suite.addTest(unittest.makeSuite(filemanagertest.FileManagerTest))
    suite.addTest(unittest.makeSuite(packagemetadatatest.PackageMetadataTest))
    suite.addTest(unittest.makeSuite(servicesmetadatatest.ServicesMetadataTest))
    suite.addTest(unittest.makeSuite(sfilemetadatatest.SFileMetadataTest))
    suite.addTest(unittest.makeSuite(snapfiletest.SnapFileTest))
    suite.addTest(unittest.makeSuite(servicedispatchertest.ServiceDispatcherTest))
    suite.addTest(unittest.makeSuite(snaptest.SnapBaseTest))
    suite.addTest(unittest.makeSuite(yumbackendtest.YumBackendTest))
    unittest.TextTestRunner(verbosity=2).run(suite)

