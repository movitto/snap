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

from snap.osregistry import OS, OSUtils
from snap.filemanager    import FileManager
from snap.metadata.sfile import SFile, FilesRecordFile

class SFileMetadataTest(unittest.TestCase):
    def setUp(self):
        self.source = ''
        self.dest = ''
        self.source_dir = ''
        self.dest_dir = ''
        
    def tearDown(self):
        if os.path.isdir(self.source_dir):
            shutil.rmtree(self.source_dir)
        if os.path.isdir(self.dest_dir):
            shutil.rmtree(self.dest_dir)
        if os.path.isfile(self.source):
            os.remove(self.source)
        if os.path.isfile(self.dest):
            os.remove(self.dest)
        
    def testWriteFilesRecordFile(self):
        path1 = os.path.join("some", "path")
        path2 = os.path.join("another", "path")
        self.dest = os.path.join(os.path.dirname(__file__), "data", "files-out.xml")
        files = [SFile(path=path1),
                  SFile(path=path2)]

        files_record_file = FilesRecordFile(self.dest)
        files_record_file.write(files)
        contents = FileManager.read_file(self.dest)

        self.assertEqual("<files><file>" + path1 + "</file><file>" + path2 + "</file></files>", contents)

    def testReadFilesRecordFile(self):
        file_path = os.path.join(os.path.dirname(__file__), "data", "recordfile.xml")
        files = FilesRecordFile(file_path).read()
        file_paths = []
        for sfile in files:
            file_paths.append(sfile.path)
        self.assertIn('/tmp/file1', file_paths)
        self.assertIn('/tmp/subdir/file2', file_paths)

    def testSFileCopyTo(self):
        basedir = os.path.join(os.path.dirname(__file__), "data")
        self.source_dir = os.path.join(basedir, "source", "subdir")
        self.dest_dir = os.path.join(basedir, "dest")

        os.makedirs(self.source_dir)
        f = open(os.path.join(self.source_dir, "foo"), 'w')
        f.write("foo")
        f.close()

        dest_file = os.path.join(self.dest_dir, self.source_dir, "foo")

        sfile = SFile(path=os.path.join(self.source_dir, "foo"))
        sfile.copy_to(self.dest_dir)
        self.assertTrue(os.path.exists(dest_file))

        contents = FileManager.read_file(dest_file)

        self.assertEqual("foo", contents)
        
        shutil.rmtree(os.path.join(basedir, "source"))

    def testSFileCopyToWithPrefix(self):
        basedir = os.path.join(os.path.dirname(__file__), "data")
        self.source_dir = os.path.join(basedir, "source", "subdir")
        self.dest_dir = os.path.join(basedir, "dest")

        os.makedirs(self.source_dir)
        f = open(os.path.join(self.source_dir, "foo"), 'w')
        f.write("foo")
        f.close()

        dest_file = os.path.join(self.dest_dir, "source", "subdir", "foo")

        sfile = SFile(path=os.path.join("source", "subdir", "foo"))
        sfile.copy_to(self.dest_dir, path_prefix=basedir)
        self.assertTrue(os.path.exists(dest_file))
        
        shutil.rmtree(os.path.join(basedir, "source"))

    @unittest.skipIf(OS.is_windows(), "symbolic links not currently supported on windows")
    def testSFileCopyLinkTo(self):     
        basedir = os.path.join(os.path.dirname(__file__), "data")
        self.source = os.path.join(basedir, "sourcelink")
        self.dest_dir = os.path.join(basedir, "destdir")

        os.makedirs(self.dest_dir)

        if os.path.islink(self.source):
            os.remove(self.source)

        os.symlink("/foobar", self.source)
        sfile = SFile(self.source)
        sfile.copy_to(self.dest_dir)

        self.assertTrue(os.path.islink(self.dest_dir + self.source))
        self.assertEqual("/foobar", os.path.realpath(self.dest_dir + self.source))

    @unittest.skipUnless(OS.is_windows(), "only needed on windows platform")
    def testSFileWindowsPathEscape(self):
        orig_path = "C:\\Program Files\\myfile"
        
        path = SFile.windows_path_escape(orig_path)
        self.assertEqual("C___Program Files\\myfile", path)
        
        path = SFile.windows_path_escape(path)
        self.assertEqual(orig_path, path)
