#!/usr/bin/python
#
# test/snaptest.py unit test for snap.SnapBase in the __init__ module
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

import os
import unittest

import snap
from snap.exceptions import SnapInsufficientPermissionError

class SnapBaseTest(unittest.TestCase):
    def setUp(self):
        self.snapbase = snap.SnapBase()
        self.snapbase.options.handlepackages = True
        self.snapbase.options.handlefiles = True

    def tearDown(self):
        pass

    def testInsufficientPermssions(self):
        restoreeuid = False
        if os.geteuid() == 0:
            restoreeuid = True
            os.seteuid(1)

        self.assertRaises(SnapInsufficientPermissionError, self.snapbase.backup)
        self.assertRaises(SnapInsufficientPermissionError, self.snapbase.restore)

        if restoreeuid:
            os.seteuid(0) 

