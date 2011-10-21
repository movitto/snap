#!/usr/bin/python
#
# test/packagestest.py unit test suite for snap.packages
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

import os, os.path, shutil
from xml.sax import make_parser
from xml.sax.handler import feature_namespaces

import unittest
import snap.files
import snap.packages

class RecordFilesTest(unittest.TestCase):
    def _clean(self):
        if os.path.exists('/tmp/snaptest'):
            if os.path.isdir('/tmp/snaptest'):
                shutil.rmtree('/tmp/snaptest')
            else:
                os.remove('/tmp/snaptest')
        os.mkdir('/tmp/snaptest')
        self.cwd = os.getcwd()
        os.chdir('test/data/')

    def _restore(self):
        os.chdir(self.cwd)

    def _make_file_parser(self, tarray):
        parser = make_parser()
        parser.setFeature(feature_namespaces, 0)
        dh = snap.files._RecordFileParser(tarray, '/')
        parser.setContentHandler(dh)
        return parser

    def _make_package_parser(self, tarray):
        parser = make_parser()
        parser.setFeature(feature_namespaces, 0)
        dh = snap.packages._PackageFileParser(tarray)
        parser.setContentHandler(dh)
        return parser

    def testFilesFromXml(self):
        self._clean()

        # perform operation we are testing
        filemanager = snap.files.FileManager('recordfile.xml', './')
        files = filemanager.restore()
        filepaths = []
        for i in files:
            filepaths.append(i.currentpath)

        # utilize the parser operation to verify results
        dfiles = []
        parser = self._make_file_parser(dfiles)
        parser.parse('recordfile.xml')
        for file in dfiles:
            if not file.currentpath in filepaths or not os.path.exists(file.currentpath):
                self._restore()
                raise Exception # recorded file not restored
            
        self._restore()

    def testXmlFromFiles(self):
        self._clean()
        
        # perform operation we are testing
        data = [snap.files.SFile('file1', 'tmp/file1', True), snap.files.SFile('file2', 'tmp/subdir/file2', True) ]
        filemanager = snap.files.FileManager('/tmp/snaprecordfile.xml', '/tmp/snaptest/')
        filemanager.backup(data)
        
        # utilize the parser operation to verify results
        dfiles,dpaths = [], []
        parser = self._make_file_parser(dfiles)
        parser.parse('/tmp/snaprecordfile.xml')
        for fle in dfiles:
            dpaths.append(fle.currentpath)
        for file in data:
            if not file.currentpath in dpaths and not os.path.exists('/tmp/snaptest/' + file.currentpath):
                raise Exception # file not copied or no record in xml

        self._restore()

    def testPackagesFromXml(self):
        self._clean()

        # perform operation we are testing
        packages = [ 'apache', 'mysql', 'kernel' ] # packages in the package file
        packagefile = snap.packages.PackageFile('packagefile.xml')
        pkgs = packagefile.read()
        pkgnms = []
        for pg in pkgs:
            pkgnms.append(pg.name)
        for pkg in packages:
            if not pkg in pkgnms:
                raise Exception # package wasn't parse from the file

        self._restore()

    def testXmlFromPackages(self):
        self._clean()
        pkgs = [ snap.packages.Package('apache'), snap.packages.Package('mysql'), snap.packages.Package('kernel') ]
        packagefile = snap.packages.PackageFile('/tmp/packagefile.xml')
        packagefile.write(pkgs)

        packages = []
        packagenames = []
        parser = self._make_package_parser(packages)
        parser.parse('/tmp/packagefile.xml')
        for pg in packages:
            packagenames.append(pg.name)

        for pkg in pkgs:
            if not pkg.name in packagenames:
                raise Exception # package not recorded in xml

        self._restore()
