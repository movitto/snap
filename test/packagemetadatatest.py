#!/usr/bin/python
#
# test/packagemetadatatest.py unit test suite for snap.metadata.package
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

from snap.filemanager import FileManager
from snap.metadata.package import Package, PackagesRecordFile

class PackageMetadataTest(unittest.TestCase):
    def testWritePackageRecordFile(self):
        file_path = os.path.join(os.path.dirname(__file__), "data/packages-out.xml")
        packages  = [Package(name='foo', version='1'),
                     Package(name='baz', version='0.1'),
                     Package(name='bar')]

        package_record_file = PackagesRecordFile(file_path)
        package_record_file.write(packages)
        contents = FileManager.read_file(file_path)

        self.assertEqual("<packages><package>foo</package><package>baz</package><package>bar</package></packages>", contents)
        os.remove(file_path)

    def testReadPackageRecordFile(self):
        file_path = os.path.join(os.path.dirname(__file__), "data/packagefile.xml")
        packages = PackagesRecordFile(file_path).read()
        package_names = []
        for package in packages:
            package_names.append(package.name)
        self.assertIn('apache', package_names)
        self.assertIn('mysql', package_names)
        self.assertIn('kernel', package_names)
