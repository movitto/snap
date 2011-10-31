#!/usr/bin/python
#
# test/aptbackendtest.py unit test suite for apt snap backends
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

import apt

import snap
import snap.backends.files.sapt
import snap.backends.repos.sapt
import snap.backends.packages.sapt

from snap.metadata.sfile   import FilesRecordFile
from snap.metadata.package import PackagesRecordFile

class AptBackendTest(unittest.TestCase):
    def setUp(self):
        self.fs_root = os.path.join(os.path.dirname(__file__), "data/fs_root")
        if os.path.isdir(self.fs_root):
            shutil.rmtree(self.fs_root)
        os.mkdir(self.fs_root)

        self.basedir = os.path.join(os.path.dirname(__file__), "data/basedir")
        if os.path.isdir(self.basedir):
            shutil.rmtree(self.basedir)
        os.mkdir(self.basedir)

    def tearDown(self):
        shutil.rmtree(self.fs_root)
        shutil.rmtree(self.basedir)

    def testBackupRepos(self):
        snapshot_target = snap.backends.repos.sapt.Sapt()
        snapshot_target.backup(self.fs_root)

        self.assertTrue(os.path.exists(self.fs_root + "/etc/apt/"))
        for afile in os.listdir("/etc/apt"):
            self.assertTrue(os.path.exists(self.fs_root + "/etc/apt/" + afile))


    def testRestoreRepos(self):
        os.makedirs(self.basedir + "/etc/apt")
        f=open(self.basedir + "/etc/apt/foo" , 'w')
        f.write("bar")
        f.close()

        restore_target = snap.backends.repos.apt.Sapt()
        restore_target.fs_root = self.fs_root
        restore_target.restore(self.basedir)

        self.assertTrue(os.path.exists(self.fs_root + self.basedir + "/etc/apt/foo"))

    def testBackupPackages(self):
        backup_target = snap.backends.packages.sapt.Sapt()
        backup_target.backup(self.fs_root)

        pkgs = []
        record = PackagesRecordFile(self.fs_root + "/packages.xml")
        record_packages = record.read()
        for pkg in record_packages:
            pkgs.append(pkg.name)

        # ensure all the system's packages have been recorded
        for pkg in apt.Cache():
            self.assertIn(pkg.sourcePackageName, pkgs)

    # TODO this test works but takes a while to execute
    def testRestorePackages(self):
        restore_target = snap.backends.packages.sapt.Sapt()
        restore_target.backup(self.fs_root)
        restore_target.fs_root = self.fs_root
        restore_target.restore(self.fs_root)

        record = PackagesRecordFile(self.fs_root + "/packages.xml")
        record_packages = record.read()

        record_package_names = []
        for pkg in record_packages:
            record_package_names.append(pkg.name)

        cache = apt.Cache()
        cache.open(None)
        for pkg in cache:
            if pkg.is_installed:
                self.assertIn(pkg.sourcePackageName, record_package_name)

    def testBackupFiles(self):
        f=open(self.fs_root + "/foo" , 'w')
        f.write("foo")
        f.close()

        backup_target = snap.backends.files.sapt.Sapt()
        backup_target.backup(self.basedir, include=[self.fs_root])

        self.assertTrue(os.path.exists(self.basedir + self.fs_root + "/foo"))

        record = FilesRecordFile(self.basedir + "/files.xml")
        files = record.read()
        file_names = []
        for sfile in files:
            file_names.append(sfile.name)
        self.assertIn("foo", file_names)
        self.assertEqual(1, len(files))

    def testBackupCertainFiles(self):
        os.mkdir(self.fs_root + "/subdir1")
        os.mkdir(self.fs_root + "/subdir1/subsubdir")
        os.mkdir(self.fs_root + "/subdir2")

        f=open(self.fs_root + "/subdir1/foo" , 'w')
        f.write("foo")
        f.close()

        f=open(self.fs_root + "/subdir2/bar" , 'w')
        f.write("bar")
        f.close()

        f=open(self.fs_root + "/subdir1/subsubdir/money" , 'w')
        f.write("money")
        f.close()

        backup_target = snap.backends.files.sapt.Sapt()
        backup_target.backup(self.basedir,
                             include=[self.fs_root + "/subdir1"],
                             exclude=[self.fs_root + "/subdir1/subsubdir"])

        self.assertTrue(os.path.exists(self.basedir  + self.fs_root + "/subdir1/foo"))
        self.assertFalse(os.path.exists(self.basedir + self.fs_root + "/subdir2/foo"))
        self.assertFalse(os.path.exists(self.basedir + self.fs_root + "/subdir1/subsubdir/money"))

        record = FilesRecordFile(self.basedir + "/files.xml")
        files = record.read()
        file_names = []
        for sfile in files:
            file_names.append(sfile.path)
        self.assertEqual(1, len(files))
        self.assertIn(self.fs_root + "/subdir1/foo", file_names)
        self.assertNotIn(self.fs_root + "/subdir2/bar", file_names)
        self.assertNotIn(self.fs_root + "/subdir1/subsubdir/bar", file_names)

    def testRestoreFiles(self):
        f=open(self.fs_root + "/foo" , 'w')
        f.write("foo")
        f.close()

        backup_target = snap.backends.files.sapt.Sapt()
        backup_target.backup(self.basedir, include=[self.fs_root])

        shutil.rmtree(self.fs_root)
        os.mkdir(self.fs_root)

        restore_target = snap.backends.files.sapt.Sapt()
        restore_target.fs_root = self.fs_root
        restore_target.restore(self.basedir)

        self.assertTrue(os.path.exists(self.fs_root + self.fs_root + "/foo"))
