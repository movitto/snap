#!/usr/bin/python
#
# test/winbackendtest.py unit test suite for windows snap backends
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
import shutil
import unittest

import snap
import snap.backends.files.win
import snap.backends.packages.win

from snap.metadata.sfile   import SFile
from snap.filemanager      import FileManager
from snap.metadata.sfile   import FilesRecordFile
from snap.metadata.package import PackagesRecordFile

class WinBackendTest(unittest.TestCase):
    def setUp(self):
        self.fs_root = os.path.join(os.path.dirname(__file__), "data", "fs_root")
        if os.path.isdir(self.fs_root):
            shutil.rmtree(self.fs_root)
        os.mkdir(self.fs_root)

        self.basedir = os.path.join(os.path.dirname(__file__), "data", "basedir")
        if os.path.isdir(self.basedir):
            shutil.rmtree(self.basedir)
        os.mkdir(self.basedir)

    def tearDown(self):
        shutil.rmtree(self.fs_root)
        shutil.rmtree(self.basedir)

    def testBackupPackages(self):
        backup_target = snap.backends.packages.win.Win()
        backup_target.backup(self.fs_root)

        pkgs = []
        record = PackagesRecordFile(os.path.join(self.fs_root, "packages.xml"))
        record_packages = record.read()
        for pkg in record_packages:
            pkgs.append(pkg.name)

        # ensure all the system's packages have been recorded
        for pkg in snap.backends.packages.win.Win.get_packages():
            self.assertIn(pkg.name, pkgs)

    def testRestorePackages(self):
        restore_target = snap.backends.packages.win.Win()
        restore_target.backup(self.basedir)
        restore_target.fs_root = self.fs_root
        restore_target.restore(self.basedir)

        win_packages = snap.backends.packages.win.Win.get_packages()

        for pkg in win_packages:
            self.assertTrue(os.path.isdir(os.path.join(self.fs_root, pkg.name)))

    def testBackupFiles(self):
        f = open(os.path.join(self.fs_root, "foo"), 'w')
        f.write("foo")
        f.close()

        backup_target = snap.backends.files.win.Win()
        backup_target.backup(self.basedir, include=[self.fs_root])

        self.assertTrue(os.path.exists(os.path.join(self.basedir, self.fs_root, "foo")))

        record = FilesRecordFile(os.path.join(self.basedir, "files.xml"))
        files = record.read()
        file_names = []
        for sfile in files:
            file_names.append(sfile.name)
        self.assertIn("foo", file_names)
        self.assertEqual(1, len(files))

    def testBackupCertainFiles(self):
        os.mkdir(os.path.join(self.fs_root, "subdir1"))
        os.mkdir(os.path.join(self.fs_root, "subdir1", "subsubdir"))
        os.mkdir(os.path.join(self.fs_root, "subdir2"))

        f = open(os.path.join(self.fs_root, "subdir1", "foo"), 'w')
        f.write("foo")
        f.close()

        f = open(os.path.join(self.fs_root, "subdir2", "bar"), 'w')
        f.write("bar")
        f.close()

        f = open(os.path.join(self.fs_root, "subdir1", "subsubdir", "money"), 'w')
        f.write("money")
        f.close()

        backup_target = snap.backends.files.win.Win()
        backup_target.backup(self.basedir,
                             include=[os.path.join(self.fs_root, "subdir1")],
                             exclude=[os.path.join(self.fs_root, "subdir1", "subsubdir")])

        self.assertTrue(os.path.exists(os.path.join(self.basedir,
                                                    SFile.windows_path_escape(os.path.join(self.fs_root, "subdir1", "foo")))))
        self.assertFalse(os.path.exists(os.path.join(self.basedir,
                                                     SFile.windows_path_escape(os.path.join(self.fs_root, "subdir2", "foo")))))
        self.assertFalse(os.path.exists(os.path.join(self.basedir,
                                                     SFile.windows_path_escape(os.path.join(self.fs_root, "subdir1", "subsubdir", "money")))))

        record = FilesRecordFile(os.path.join(self.basedir, "files.xml"))
        files = record.read()
        file_names = []
        for sfile in files:
            file_names.append(sfile.path)
        self.assertEqual(1, len(files))
        self.assertIn(SFile.windows_path_escape(os.path.join(self.fs_root, "subdir1", "foo")), file_names)
        self.assertNotIn(SFile.windows_path_escape(os.path.join(self.fs_root, "subdir2", "bar")), file_names)
        self.assertNotIn(SFile.windows_path_escape(os.path.join(self.fs_root, "subdir1", "subsubdir", "bar")), file_names)

    def testRestoreFiles(self):
        f = open(os.path.join(self.fs_root, "foo"), 'w')
        f.write("foo")
        f.close()

        backup_target = snap.backends.files.win.Win()
        backup_target.backup(self.basedir, include=[self.fs_root])

        shutil.rmtree(self.fs_root)
        os.mkdir(self.fs_root)

        restore_target = snap.backends.files.win.Win()
        restore_target.fs_root = self.fs_root
        restore_target.restore(self.basedir)

        self.assertTrue(os.path.exists(os.path.join(self.fs_root, self.fs_root, "foo")))
