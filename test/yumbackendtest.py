#!/usr/bin/python
#
# test/sfilemetadatatest.py unit test suite for snap.metadata.sfile
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

class YumBackendTest(unittest.TestCase):
    def testBackupRepos(self):
        fs_root = os.path.join(os.path.dirname(__file__), "data/fs_root")
        os.path.mkdir(fs_root)

        snapshot_target = snap.backends.repos.yum.Yum()
        snapshot_target.backup(fs_root)

        self.assertTrue(os.path.exists(fs_root + "/etc/yum.conf"))
        for repo in os.listdir("/etc/yum.repos.d"):
            self.assertTrue(os.path.exists(fs_root + repo))

        os.remove(fs_root)


    def testRestoreRepos(self):
        fs_root = os.path.join(os.path.dirname(__file__), "data/fs_root")
        os.path.mkdir(fs_root)

        basedir = os.path.join(os.path.dirname(__file__), "data/basedir")
        os.path.makedirs(basedir + "/etc/yum.repos.d")
        f=open(basedir + "/etc/yum.conf" , 'w')
        f.write("foo")
        f.close()
        f=open(basedir + "/etc/yum.repos.d/foo.repo" , 'w')
        f.write("bar")
        f.close()

        restore_target = snap.backends.repos.yum.Yum()
        restore_target.fs_root = fs_root
        snapshot_target.restore(basedir)

        self.assertTrue(os.path.exists(fs_root + "/etc/yum.conf"))
        self.assertTrue(os.path.exists(fs_root + "/etc/yum.repos.d/foo.repo"))

        os.remove(fs_root)
        os.remove(basedir)

    def testBackupPackages(self):
        fs_root = os.path.join(os.path.dirname(__file__), "data/fs_root")
        os.path.mkdir(fs_root)

        backup_target = snap.backends.packages.yum.Yum()
        backup_target.backup(fs_root)

        pkgs = []
        record = PackagesRecordFile(fs_root + "packages.xml")
        record_packages = record.read()
        for pkg in record_packages:
            pkgs.append(pkg.name)

        # ensure all the system's packages have been recorded
        for pkg in yum.YumBase().rpmdb:
            self.assertIn(pkg.name, pkgs)

        os.remove(fs_root)

    def testRestorePackages(self):
        fs_root = os.path.join(os.path.dirname(__file__), "data/fs_root")
        os.path.mkdir(fs_root)

        restore_target = snap.backends.packages.yum.Yum()
        restore_target.backup(fs_root)
        restore_target.restore(fs_root)

        record = PackagesRecordFile(fs_root + "packages.xml")
        record_packages = record.read()

        yum = yum.YumBase()
        yum.rpmdb.dbpath = fs_root + '/var/lib/rpm'
        
        for pkg in record_packages:
            self.assertIn(pkg, yum.rpmdb)

        os.remove(fs_root)

    def testBackupFiles(self):
        fs_root = os.path.join(os.path.dirname(__file__), "data/fs_root")
        os.path.mkdir(fs_root)

        basedir = os.path.join(os.path.dirname(__file__), "data/basedir")
        os.path.mkdir(basedir)

        f=open(fs_root + "/foo" , 'w')
        f.write("foo")
        f.close()

        backup_target = snap.backends.files.yum.Yum()
        backup_target.backup(basedir, include=[fs_root])

        self.assertTrue(os.path.exists(basedir + "/foo"))

        record = FilesRecordFile(basedir + "files.xml")
        files = record.read()
        file_names = []
        for sfile in files:
            file_name.append(sfile.name)
        self.assertIn("foo", file_name)
        self.assertEqual(1, files.size())

        os.remove(fs_root)
        os.remove(basedir)

    def testRestoreFiles(self):
        fs_root = os.path.join(os.path.dirname(__file__), "data/fs_root")
        os.path.mkdir(fs_root)

        basedir = os.path.join(os.path.dirname(__file__), "data/basedir")
        os.path.mkdir(basedir)

        f=open(fs_root + "/foo" , 'w')
        f.write("foo")
        f.close()

        backup_target = snap.backends.files.yum.Yum()
        backup_target.backup(basedir, include=[fs_root])

        os.remove(fs_root)
        os.path.mkdir(fs_root)

        restore_target = snap.backends.files.yum.Yum()
        restore_target.fs_root = fs_root
        restore_target.restore(basedir)

        self.assertTrue(os.path.exists(fs_root + "/foo"))
