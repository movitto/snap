#!/usr/bin/python
#
# The 'snap package file' format and how to construct/parse it
#
# (C) Copyright 2007 Mohammed Morsi (movitto@yahoo.com)
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

from xml.sax import make_parser
from xml.sax import handler,saxutils
from xml.sax.handler import feature_namespaces

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

# file operations on a package file
class PackageFile:
    '''a snap package record file, contains list of packages installed, to restore'''
    
    # Name of the package file which we are reading / writing
    packagefile=None

    def __init__(self, filename):
        '''initialize the file

        @param filename - path to the file 
        '''

        self.packagefile = filename

    def read(self):
        '''
        read packages from the file

        @returns - list of instances of Package
        '''

        packages=[]
        parser = make_parser()
        parser.setFeature(feature_namespaces, 0)
        dh = _PackageFileParser(packages)
        parser.setContentHandler(dh)
        parser.parse(self.packagefile)
        snap.callback.snapcallback.restore_packages()
        return packages
        
    def write(self, packages):
        '''
        write packages to the file

        @param packages - list of instances of Package
        '''

        snap.callback.snapcallback.backup_packages()
        f=open(self.packagefile, 'w')
        f.write("<packages>\n")
        for package in packages:
            snap.callback.snapcallback.backup_package(package)
            f.write(' <package>\n')
            f.write('  <name>' + saxutils.escape(package.name) + '</name>\n');
            f.write(' </package>\n')
        f.write("</packages>\n")
        f.close()


# internal class to parse the record file xml
#class _PackageFileParser(saxutils.DefaultHandler):
class _PackageFileParser(handler.ContentHandler):
    # list of packages parsed
    packages=None

    # current package being processed
    package=None

    # flag indicating if we are evaluating a name
    inNameContent=False
    
    def __init__(self, packages):
        self.packages = packages

    def startElement(self, name, attrs):
        if name == 'package':
            self.package = Package()
            self.packages.append(self.package)
        elif name == 'name':
            self.inNameContent=True

    def characters(self, ch):
        if self.inNameContent:
            self.package.name = self.package.name + ch

    def endElement(self, name):
        if name == 'name':
            self.package.name = saxutils.unescape(self.package.name)
            snap.callback.snapcallback.restore_package(self.package)
            self.inNameContent=False
