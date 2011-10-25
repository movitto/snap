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

import os
import unittest

from snap.metadata.sfile import SFile, FilesRecordFile

class SFileMetadataTest(unittest.TestCase):
    def testWriteFilesRecordFile(self):
        file_path = os.path.join(os.path.dirname(__file__), "data/files-out.xml")
        files  = [SFile(path='/some/path'),
                  SFile(path='/another/path')]

        files_record_file = FilesRecordFile(file_path)
        files_record_file.write(files)
        f=open(file_path, 'r')
        contents = f.read()
        f.close()

        self.assertEqual("<files><file>/some/path</file><file>/another/path</file></files>", contents)

    def testReadFilesRecordFile(self):
        file_path = os.path.join(os.path.dirname(__file__), "data/recordfile.xml")
        files = FilesRecordFile(file_path).read()
        file_paths = []
        for sfile in files:
            file_paths.append(sfile.path)
        self.assertIn('/tmp/file1', file_paths)
        self.assertIn('/tmp/subdir/file2', file_paths)

    def testSFileCopyTo(self):
        basedir   = os.path.join(os.path.dirname(__file__), "data")
        source_dir = basedir + "/source/subdir/"
        dest_dir   = basedir + "/dest/"
        temp_file_path = source_dir + "foo"
        os.makedirs(source_dir)

        f=open(temp_file_path, 'w')
        f.write("foo")
        f.close()

        sfile = SFile(path=temp_file_path)
        sfile.copy_to(basedir)
        self.assertTrue(os.path.exists(temp_file_path))

        f=open(temp_file_path, 'r')
        contents = f.read()
        f.close()

        self.assertEqual("foo", contents)

        sfile = SFile(path="/source/subdir/foo")
        sfile.copy_to(dest_dir, path_prefix=basedir)
        self.assertTrue(os.path.exists(temp_file_path))

        os.remove(temp_file_path)
        os.removedirs(source_dir)
