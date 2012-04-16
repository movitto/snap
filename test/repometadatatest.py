#!/usr/bin/python
#
# test/repometadatatest.py unit test suite for snap.metadata.repo
#
# (C) Copyright 2012 Mo Morsi (mo@morsi.org)
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

from snap.filemanager import FileManager
from snap.metadata.repo import Repo, ReposRecordFile

class RepoMetadataTest(unittest.TestCase):
    def testWriteReposRecordFile(self):
        file_path = os.path.join(os.path.dirname(__file__), "data/repos-out.xml")
        repos  = [Repo(name='yum.morsi.org', url='http://yum.morsi.org'),
                  Repo(name='apt.morsi.org', url='http://apt.morsi.org')]

        repo_record_file = ReposRecordFile(file_path)
        repo_record_file.write(repos)
        contents = FileManager.read_file(file_path)

        self.assertEqual("<repos><repo>http://yum.morsi.org</repo><repo>http://apt.morsi.org</repo></repos>", contents)
        os.remove(file_path)

    def testReadReposRecordFile(self):
        file_path = os.path.join(os.path.dirname(__file__), "data/repos.xml")
        repos = ReposRecordFile(file_path).read()
        repo_urls = []
        for repo in repos:
            repo_urls.append(repo.url)
        self.assertIn('http://yum.morsi.org', repo_urls)
        self.assertIn('http://apt.morsi.org', repo_urls)
