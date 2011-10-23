#!/usr/bin/python
#
# test/filemanagertest.py unit test suite for snap.filemanager
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

import unittest

class FileManagerTest(unittest.TestCase):
    def testRmAndExists(self):
        temp_file_path = os.path.join(os.path.dirname(__file__), "data/temp-file")

        f=open(temp_file_path, 'w')
        f.write("foo")
        f.close()
        self.assertTrue(os.path.exists(temp_file_path))
        self.assertTrue(os.path.isfile(temp_file_path))
        self.assertTrue(FileManager.exists(temp_file_path))

        FileManager.rm(temp_file_path)
        self.assertFalse(os.path.exists(temp_file_path))
        self.assertFalse(FileManager.exists(temp_file_path))
        pass

    def testMakeDirAndExists(self):
        temp_dir_path = os.path.join(os.path.dirname(__file__), "data/temp-dir")

        FileManager.mkdir(temp_dir_path)
        self.assertTrue(os.path.exists(temp_dir_path))
        self.assertTrue(os.path.isdir(temp_dir_path))
        self.assertTrue(FileManager.exists(temp_dir_path))
        
        os.remove(temp_dir_path)
        self.assertFalse(os.path.exists(temp_dir_path))
        self.assertFalse(FileManager.exists(temp_dir_path))

    def testGetAllFiles(self):
        data_path = os.path.join(os.path.dirname(__file__), "data/tmp")
        files = FileManager.get_all_files(include_dirs=[data_path])
        self.assertIn(data_path + "file1", files)
        self.assertIn(data_path + "subdir/file2", files)

        files = FileManager.get_all_files(include_dirs=[data_path], exclude_dirs=[data_path+'subdir'])
        self.assertIn(data_path + "file1", files)
        self.assertNotIn(data_path + "subdir/file2", files)

    def testGetAllSubdirectories(self):
        data_path = os.path.join(os.path.dirname(__file__), "data/")
        subdirs = FileManager.get_all_subdirectories(data_path, recursive=True)
        self.assertIn("tmp", subdirs)
        self.assertIn("tmp/subdir", subdirs)

        subdirs = FileManager.get_all_subdirectories(data_path, recursive=False)
        self.assertIn("tmp", subdirs)
        self.assertNotIn("tmp/subdir", subdirs)
