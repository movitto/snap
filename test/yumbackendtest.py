#!/usr/bin/python
#
# test/yumbackendtest.py unit test suite for yum snap backends
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

import yum

import snap
import snap.backends.files.syum
import snap.backends.repos.syum
import snap.backends.packages.syum

from snap.filemanager      import FileManager
from snap.metadata.sfile   import FilesRecordFile
from snap.metadata.package import PackagesRecordFile

from snap.packageregistry  import PackageRegistry

class YumBackendTest(unittest.TestCase):
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
        snapshot_target = snap.backends.repos.syum.Syum()
        snapshot_target.backup(self.fs_root)

        self.assertTrue(os.path.exists(self.fs_root + "/etc/yum.conf"))
        for repo in os.listdir("/etc/yum.repos.d"):
            self.assertTrue(os.path.exists(self.fs_root + "/etc/yum.repos.d/" + repo))


    def testRestoreRepos(self):
        os.makedirs(self.basedir + "/etc/yum.repos.d")
        f=open(self.basedir + "/etc/yum.conf" , 'w')
        f.write("foo")
        f.close()
        f=open(self.basedir + "/etc/yum.repos.d/foo.repo" , 'w')
        f.write("bar")
        f.close()

        restore_target = snap.backends.repos.syum.Syum()
        restore_target.fs_root = self.fs_root
        restore_target.restore(self.basedir)


        self.assertTrue(os.path.exists(self.fs_root + "/etc/yum.conf"))
        self.assertTrue(os.path.exists(self.fs_root + "/etc/yum.repos.d/foo.repo"))

    def testBackupPackages(self):
        backup_target = snap.backends.packages.syum.Syum()
        backup_target.backup(self.fs_root)

        pkgs = []
        record = PackagesRecordFile(self.fs_root + "/packages.xml")
        record_packages = record.read()
        for pkg in record_packages:
            pkgs.append(pkg.name)

        # ensure all the system's packages have been encoded and recorded
        for pkg in yum.YumBase().rpmdb:
            encoded = PackageRegistry.encode('yum', pkg.name)
            self.assertIn(encoded, pkgs)

    def testRestorePackages(self):
        restore_target = snap.backends.packages.syum.Syum()
        restore_target.backup(self.fs_root)
        restore_target.fs_root = self.fs_root
        restore_target.restore(self.fs_root)

        record = PackagesRecordFile(self.fs_root + "/packages.xml")
        record_packages = record.read()

        record_package_names = []
        for pkg in record_packages:
            record_package_names.append(pkg.name)

        installed_package_names = []
        lyum = yum.YumBase()
        lyum.rpmdb.dbpath = self.fs_root + '/var/lib/rpm'
        for pkg in lyum.rpmdb:
            installed_package_names.append(pkg.name)

        for pkg in record_package_names:
            decoded = PackageRegistry.decode('yum', pkg)
            self.assertIn(decoded, installed_package_names)

    def testBackupFiles(self):
        f=open(self.fs_root + "/foo" , 'w')
        f.write("foo")
        f.close()

        backup_target = snap.backends.files.syum.Syum()
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

        backup_target = snap.backends.files.syum.Syum()
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
        self.assertIn(self.fs_root[1:] + "/subdir1/foo", file_names)
        self.assertNotIn(self.fs_root[1:] + "/subdir2/bar", file_names)
        self.assertNotIn(self.fs_root[1:] + "/subdir1/subsubdir/bar", file_names)

    def testRestoreFiles(self):
        f=open(self.fs_root + "/foo" , 'w')
        f.write("foo")
        f.close()

        backup_target = snap.backends.files.syum.Syum()
        backup_target.backup(self.basedir, include=[self.fs_root])

        shutil.rmtree(self.fs_root)
        os.mkdir(self.fs_root)

        restore_target = snap.backends.files.syum.Syum()
        restore_target.fs_root = self.fs_root
        restore_target.restore(self.basedir)

        self.assertTrue(os.path.exists(self.fs_root + self.fs_root + "/foo"))
