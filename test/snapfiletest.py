#!/usr/bin/python
#
# test/snapfiletest.py unit test suite for snap.metadata.snapfile
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
import tarfile
import unittest

from snap.exceptions  import MissingDirError
from snap.metadata.snapfile import SnapFile

class SnapFileTest(unittest.TestCase):
    def testInvalidSnapdirectoryShouldRaiseError(self):
        with self.assertRaises(MissingDirError) as context:
            SnapFile('foo', '/invalid/dir')
        self.assertEqual(context.exception.message, '/invalid/dir is an invalid snap working directory ')

    def testCompressSnapFile(self):
        snapdir = os.path.join(os.path.dirname(__file__), "data")
        snapfile = SnapFile(os.path.join(snapdir, "test-snapfile.tgz"), snapdir)
        snapfile.compress()

        tarball = tarfile.open(os.path.join(snapdir, "test-snapfile.tgz"), "r:gz")
        files = []
        for tarinfo in tarball:
            files.append(tarinfo.name)
        self.assertIn(os.path.join("tmp", "file1"), files)
        self.assertIn(os.path.join("tmp", "subdir", "file2"), files)

        #os.remove(os.path.join(snapdir, "test-snapfile.tgz"))

    def testExtractSnapFile(self):
        snap_file_path = os.path.join(os.path.dirname(__file__), "data/existing-snapfile.tgz")
        snapdir = os.path.join(os.path.dirname(__file__), "data/new-snapdir/")
        os.makedirs(snapdir)
        snapfile = SnapFile(snap_file_path, snapdir)
        snapfile.extract()

        self.assertTrue(os.path.exists(snapdir + "packagefile.xml"))
        self.assertTrue(os.path.exists(snapdir + "recordfile.xml"))

        os.remove(snapdir + "packagefile.xml")
        os.remove(snapdir + "recordfile.xml")
        os.removedirs(snapdir)
