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
import shutil
import unittest

from snap.filemanager    import FileManager
from snap.metadata.sfile import SFile, FilesRecordFile

class SFileMetadataTest(unittest.TestCase):
    def testWriteFilesRecordFile(self):
        file_path = os.path.join(os.path.dirname(__file__), "data/files-out.xml")
        files  = [SFile(path='/some/path'),
                  SFile(path='/another/path')]

        files_record_file = FilesRecordFile(file_path)
        files_record_file.write(files)
        contents = FileManager.read_file(file_path)

        self.assertEqual("<files><file>/some/path</file><file>/another/path</file></files>", contents)
        os.remove(file_path)

    def testReadFilesRecordFile(self):
        file_path = os.path.join(os.path.dirname(__file__), "data/recordfile.xml")
        files = FilesRecordFile(file_path).read()
        file_paths = []
        for sfile in files:
            file_paths.append(sfile.path)
        self.assertIn('/tmp/file1', file_paths)
        self.assertIn('/tmp/subdir/file2', file_paths)

    def testSFileCopyTo(self):
        basedir    = os.path.join(os.path.dirname(__file__), "data")
        source_dir = basedir + "/source/subdir"
        dest_dir   = basedir + "/dest"

        os.makedirs(source_dir)
        f=open(source_dir + "/foo", 'w')
        f.write("foo")
        f.close()

        dest_file = dest_dir + source_dir + "/foo"

        sfile = SFile(path=source_dir + "/foo")
        sfile.copy_to(dest_dir)
        self.assertTrue(os.path.exists(dest_file))

        contents = FileManager.read_file(dest_file)

        self.assertEqual("foo", contents)

        shutil.rmtree(source_dir)
        shutil.rmtree(dest_dir)

    def testSFileCopyToWithPrefix(self):
        basedir    = os.path.join(os.path.dirname(__file__), "data")
        source_dir = basedir + "/source/subdir"
        dest_dir   = basedir + "/dest"

        os.makedirs(source_dir)
        f=open(source_dir + "/foo", 'w')
        f.write("foo")
        f.close()

        dest_file = dest_dir + "/source/subdir/foo"

        sfile = SFile(path="/source/subdir/foo")
        sfile.copy_to(dest_dir, path_prefix=basedir)
        self.assertTrue(os.path.exists(dest_file))

        shutil.rmtree(source_dir)
        shutil.rmtree(dest_dir)

    def testSFileCopyLinkTo(self):
        basedir    = os.path.join(os.path.dirname(__file__), "data")
        source     = basedir + "/sourcelink"
        destdir    = basedir + "/destdir"

        os.makedirs(destdir)

        os.symlink("/foobar", source)
        sfile = SFile(source)
        sfile.copy_to(destdir)

        self.assertTrue(os.path.islink(destdir + source))
        self.assertEqual("/foobar", os.path.realpath(destdir + source))

        shutil.rmtree(destdir)
        os.remove(source)
