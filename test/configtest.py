#!/usr/bin/python
#
# test/configtest.py unit test suite for snap.configmanager.ConfigurationManager
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
from snap.configmanager import ConfigManager, ConfigOptions
from snap.exceptions import SnapArgError

class ConfigManagerTest(unittest.TestCase):
    # specific option validation

    def testValidateMode(self):
        # ensure that if mode is not set, exception is thrown
        co = ConfigOptions()
        cm = ConfigManager(co)
        self.assertRaises(SnapArgError, cm.verify_integrity)
        pass

    def testValidateRestoreSnapFile(self):
        # ensure that if snap is in restore mode and snapfile
        # is not set, error is thrown
        co = ConfigOptions()
        co.mode = co.RESTORE
        cm = ConfigManager(co)
        self.assertRaises(SnapArgError, cm.verify_integrity)
        pass
