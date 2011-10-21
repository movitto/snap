#!/usr/bin/python
#
# Metadata pertaining to packages backed up / restored by Snap!
#
# (C) Copyright 2011 Mo Morsi (mo@morsi.org)
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

import snap

class Package:
    """information about a package tracked by snap"""

    name=''
    version=''
    def __init__(self, name='', version=''):
        '''initialize the package

        @param name - the name of the package
        @param version - version of the package, currently not used
        '''

        self.name = name
        self.version = version

class PackagesRecordFile:
    '''a snap package record file, contains list of packages installed, to restore'''
    
    def __init__(self, record_file):
        '''initialize the file

        @param filename - path to the file 
        '''

        self.packagefile = filename

    def write(self, packages):
        '''generate file containing record of packages

        @param packages - list of Packages to record
        '''
        f=open(self.packagefile, 'w')
        f.write("<packages>\n")
        for package in packages:
            f.write(' <package>\n  ' + saxutils.escape(package.name) + '\n </package>\n');
        f.write("</packages>\n")
        f.close()

    def read(self):
        '''
        read packages from the file

        @returns - list of instances of Package
        '''
        parser = xml.sax.handler.make_parser()
        parser.setFeature(xml.sax.handler.feature_namespaces, 0)
        handler = _PackageFileParser(packages)
        parser.setContentHandler(handler)
        parser.parse(self.packagefile)
        return handler.packages
        


# internal class to parse the record file xml
#class _PackageFileParser(saxutils.DefaultHandler):
class _PackagesRecordFileParser(handler.ContentHandler):
    # list of packages parsed
    packages=[]

    # current package being processed
    current_package=None

    # flag indicating if we are evaluating a name
    in_package_content=False
    
    def startElement(self, name, attrs):
        if name == 'package':
            self.current_package = ''
            self.in_package_content=True

    def characters(self, ch):
        if self.in_package_content:
            self.current_package = self.current_package + ch

    def endElement(self, name):
        if name == 'package':
            self.in_package_content = False
            packages.append(Package(name=saxutils.unescape(self.current_package)))
