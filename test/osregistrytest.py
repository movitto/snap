#!/usr/bin/python
#
# test/osregistrytest.py unit test suite for snap.osregistry
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
import re
import shutil
import unittest
import tempfile
import subprocess

from snap.osregistry import OS, OSUtils

class OsRegistryTest(unittest.TestCase):
    def setUp(self):
        self.basedir = os.path.join(os.path.dirname(__file__), "data", "osrtest")
        if not os.path.isdir(self.basedir):
            os.mkdir(self.basedir)
    
    def tearDown(self):
        if os.path.isdir(self.basedir):
            shutil.rmtree(self.basedir)

    def testIsLinux(self):
        self.assertTrue(OS.is_linux('fedora'))
        self.assertTrue(OS.is_linux('rhel'))
        self.assertTrue(OS.is_linux('centos'))
        self.assertTrue(OS.is_linux('ubuntu'))
        self.assertTrue(OS.is_linux('debian'))
        self.assertTrue(OS.is_linux('mock'))
        self.assertFalse(OS.is_linux('windows'))
        self.assertFalse(OS.is_linux('mock_windows'))

    def testIsWindows(self):
        self.assertFalse(OS.is_windows('fedora'))
        self.assertFalse(OS.is_windows('rhel'))
        self.assertFalse(OS.is_windows('centos'))
        self.assertFalse(OS.is_windows('ubuntu'))
        self.assertFalse(OS.is_windows('debian'))
        self.assertFalse(OS.is_windows('mock'))
        self.assertTrue(OS.is_windows('windows'))
        self.assertTrue(OS.is_windows('mock_windows'))
        
    def testAptBased(self):
        self.assertTrue(OS.apt_based('ubuntu'))
        self.assertTrue(OS.apt_based('debian'))
        self.assertFalse(OS.apt_based('fedora'))
        self.assertFalse(OS.apt_based('rhel'))
        self.assertFalse(OS.apt_based('centos'))
        self.assertFalse(OS.apt_based('windows'))
        
    def testYumBased(self):
        self.assertFalse(OS.yum_based('ubuntu'))
        self.assertFalse(OS.yum_based('debian'))
        self.assertTrue(OS.yum_based('fedora'))
        self.assertTrue(OS.yum_based('rhel'))
        self.assertTrue(OS.yum_based('centos'))
        self.assertFalse(OS.yum_based('windows'))
        
    def testOsRoot(self):
        self.assertEqual('/', OS.get_root('fedora'))
        self.assertEqual('/', OS.get_root('ubuntu'))
        self.assertEqual('C:\\', OS.get_root('windows'))
        
    @unittest.skipUnless(OS.is_windows(), "only relevant for windows")
    def testWindowsRoot(self):
        self.assertEqual('C:\\', OS.get_root())
        
    @unittest.skipUnless(OS.is_linux(), "only relevant for linux")
    def testLinuxRoot(self):
        self.assertEqual('/', OS.get_root())

    def testPathSeperator(self):
        self.assertEqual('/', OS.get_path_seperator('fedora'))
        self.assertEqual('/', OS.get_path_seperator('ubuntu'))
        self.assertEqual('\\', OS.get_path_seperator('windows'))
        
    @unittest.skipUnless(OS.is_windows(), "only relevant for windows")
    def testWindowsPathSeperator(self):
        self.assertEqual('\\', OS.get_path_seperator())
        
    @unittest.skipUnless(OS.is_linux(), "only relevant for linux")
    def testLinuxPathSeperator(self):
        self.assertEqual('/', OS.get_path_seperator())

    #def testDefaultBackendForTarget(self):
    
    @unittest.skipUnless(OS.is_windows(), "only relevant for windows")
    def testWindowsNullFile(self):
        self.assertEqual("nul", OSUtils.null_file())
        
    @unittest.skipUnless(OS.is_linux(), "only relevant for linux")
    def testLinuxNullFile(self):
        self.assertEqual("/dev/null", OSUtils.null_file())
        
    @unittest.skipUnless(OS.is_windows(), "only relevant for windows")
    def testWindowsChown(self):
        basefile = os.path.join(self.basedir, "foo")
        f = open(basefile, "w")
        f.write("foo")
        f.close
        OSUtils.chown(self.basedir, username="mmorsi")

        null = open(OSUtils.null_file(), 'w')
        tfile = tempfile.TemporaryFile()
        popen = subprocess.Popen(["icacls", self.basedir], stdout=tfile, stderr=null)
        popen.wait()
        tfile.seek(0)
        c = tfile.read()
        self.assertNotEqual(1, len(re.findall(".*mmorsi.*(F).*\n.*", c))) 
        tfile.close()

        tfile = tempfile.TemporaryFile()
        popen = subprocess.Popen(["icacls", basefile], stdout=tfile, stderr=null)
        popen.wait()
        tfile.seek(0)
        c = tfile.read()
        self.assertNotEqual(1, len(re.findall(".*mmorsi.*(F).*\n.*", c)))
        tfile.close()

    @unittest.skipUnless(OS.is_linux(), "only relevant for linux")
    def testLinuxChown(self):
        basefile = os.path.join(self.basedir, "foo")
        f = open(basefile, "w")
        f.write("foo")
        f.close
        OSUtils.chown(self.basedir, uid=100, gid=100)
        
        st = os.stat(self.basedir)
        self.assertEqual(100, st.st_uid)
        self.assertEqual(100, st.st_gid)
        st = os.stat(basefile)
        self.assertEqual(100, st.st_uid)
        self.assertEqual(100, st.st_gid)
        
        import pwd
        pwo = pwd.getpwnam("nobody")
        uid = pwo.pw_uid
        gid = pwo.pw_gid
        OSUtils.chown(self.basedir, username="nobody")
        st = os.stat(self.basedir)
        self.assertEqual(uid, st.st_uid)
        self.assertEqual(gid, st.st_gid)
        st = os.stat(basefile)
        self.assertEqual(uid, st.st_uid)
        self.assertEqual(gid, st.st_gid)
    
    #@unittest.skipUnless(OS.is_windows(), "only relevant for windows")
    #def testWindowsIsSuperUser(self):
    # not sure how to switch users on windows to test this
    
    @unittest.skipUnless(OS.is_linux(), "only relevant for linux")
    def testLinuxIsSuperUser(self):
        ouid = os.geteuid()
        self.assertTrue(OSUtils.is_superuser())
        
        os.seteuid(100)
        self.assertFalse(OSUtils.is_superuser())
        
        os.seteuid(ouid)
