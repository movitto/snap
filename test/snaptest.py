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
import types
import unittest

import snap
from snap.exceptions import InsufficientPermissionError
from snap.osregistry import OS

class SnapBaseTest(unittest.TestCase):
    def setUp(self):
        self.snapbase = snap.SnapBase()

        self.orig_os_lookup = OS.lookup
        OS.lookup = types.MethodType(SnapBaseTest.new_os_lookup, OS)

        self.orig_target_backends = snap.config.options.target_backends
        snap.config.options.target_backends = {'repos'    : True,
                                               'packages' : True,
                                               'files'    : True }

        self.orig_snapfile = snap.config.options.snapfile
        snap.config.options.snapfile += "-snap-test.tgz"

    def tearDown(self):
        OS.lookup = self.orig_os_lookup
        snap.config.target_backends  = self.orig_target_backends
        snap.config.options.snapfile = self.orig_snapfile

    def testInsufficientPermssions(self):
        restoreeuid = False
        if os.geteuid() == 0:
            restoreeuid = True
            os.seteuid(1)

        with self.assertRaises(InsufficientPermissionError):
            self.snapbase.backup()
        with self.assertRaises(InsufficientPermissionError):
            self.snapbase.restore()

        if restoreeuid:
            os.seteuid(0) 

    def new_os_lookup(self):
        return 'mock'
    new_os_lookup=staticmethod(new_os_lookup)

    def testLoadBackends(self):
        backends = self.snapbase.load_backends()
        backend_classes = []
        for backend in backends:
            backend_classes.append(backend.__class__)

        self.assertEqual('mock', snap.config.options.target_backends['repos'])
        self.assertEqual('mock', snap.config.options.target_backends['packages'])
        self.assertEqual('mock', snap.config.options.target_backends['files'])

        self.assertIn(snap.backends.repos.mock.Mock,    backend_classes)
        self.assertIn(snap.backends.packages.mock.Mock, backend_classes)
        self.assertIn(snap.backends.files.mock.Mock,    backend_classes)


    def testBackup(self):
        self.snapbase.backup()

        self.assertTrue(snap.backends.repos.mock.Mock.backup_called)
        self.assertTrue(snap.backends.packages.mock.Mock.backup_called)
        self.assertTrue(snap.backends.files.mock.Mock.backup_called)

        self.assertTrue(os.path.exists(snap.config.options.snapfile))
        os.remove(snap.config.options.snapfile)


    def testRestore(self):
        # to generate the snapfile
        self.snapbase.backup()

        self.snapbase.restore()

        self.assertTrue(snap.backends.repos.mock.Mock.restore_called)
        self.assertTrue(snap.backends.packages.mock.Mock.restore_called)
        self.assertTrue(snap.backends.files.mock.Mock.restore_called)

        os.remove(snap.config.options.snapfile)
