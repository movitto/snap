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

import unittest

class PackageMetadataTest(unittest.TestCase):
    def testWritePackageRecordFile(self):
        file_path = os.path.join(os.path.dirname(__file__), "data/packages-out.xml")
        packages  = [Package(name='foo', version='1'),
                     Package(name='baz', version='0.1'),
                     Package(name='bar')]

        package_record_file = PackageRecordFile(file_path)
        package_record_file.write(packages)
        f=open(file_path, 'r')
        contents = f.read()
        f.close()

        self.assertEqual("<packages>\n<package>foo</package>\n<package>bar</package>\n<package>bar</package></packages>", contents)

    def testReadPackageRecordFile(self):
        file_path = os.path.join(os.path.dirname(__file__), "data/packagefile.xml")
        packages = PackageRecordFile(file_path).read()
        self.assertIn('apache', packages)
        self.assertIn('mysql', packages)
        self.assertIn('kernel', packages)
