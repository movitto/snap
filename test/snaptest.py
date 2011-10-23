#!/usr/bin/python
#
# test/snaptest.py unit test for snap.SnapBase in the __init__ module
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

import os
import unittest

import snap
from snap.exceptions import InsufficientPermissionError

class SnapBaseTest(unittest.TestCase):
    def setUp(self):
        self.snapbase = snap.SnapBase(snapfile_id='snap-test')

        self.orig_os_lookup = OS.lookup
        OS.lookup = SnapBaseTest.new_os_lookup

        self.orig_target_backends = self.config.options.target_backends
        snap.config.options.target_backends = {'repos'    => True,
                                               'packages' => True,
                                               'files'    => True }

    def tearDown(self):
        OS.lookup = self.orig_os_lookup
        snap.config.target_backends = self.orig_target_backends

    def testInsufficientPermssions(self):
        restoreeuid = False
        if os.geteuid() == 0:
            restoreeuid = True
            os.seteuid(1)

        self.assertRaises(InsufficientPermissionError, self.snapbase.backup())
        self.assertRaises(InsufficientPermissionError, self.snapbase.restore())

        if restoreeuid:
            os.seteuid(0) 

    def new_os_lookup(self):
        return 'mock'

    def testLoadBackends(self):
        backends = self.snapbase.load_backends()
        self.assertEqual('mock', snap.config.options.target_backends['repos'])
        self.assertEqual('mock', snap.config.options.target_backends['packages'])
        self.assertEqual('mock', snap.config.options.target_backends['files'])
        self.assertEqual(globals()["snap.backends.repos.Mock"],    snap.backends.repos.Mock)
        self.assertEqual(globals()["snap.backends.packages.Mock"], snap.backends.repos.Mock)
        self.assertEqual(globals()["snap.backends.files.Mock"],    snap.backends.repos.Mock)

        self.assertIn(snap.backends.repos.Mock,    backends)
        self.assertIn(snap.backends.packages.Mock, backends)
        self.assertIn(snap.backends.files.Mock,    backends)


    def testBackup(self):
        self.snapbase.backup()

        self.assertTrue(snap.backends.repos.Mock.backup_called)
        self.assertTrue(snap.backends.packages.Mock.backup_called)
        self.assertTrue(snap.backends.files.Mock.backup_called)

        self.assertTrue(os.path.exists(snap.config.options.snapfile + "-snap-test.tgz")
        os.remove(snap.config.options.snapfile + "-snap-test.tgz")


    def testRestore(self):
        # to generate the snapfile
        self.snapbase.backup()

        self.config.options.snapfile = snap.config.options.snapfile + "-snap-test.tgz"
        self.snapbase.restore()

        self.assertTrue(snap.backends.repos.Mock.restore_called)
        self.assertTrue(snap.backends.packages.Mock.restore_called)
        self.assertTrue(snap.backends.files.Mock.restore_called)

        os.remove(snap.config.options.snapfile)
