#!/usr/bin/python
#
# Metadata pertaining to packages backed up / restored by Snap!
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

import xml, xml.sax, xml.sax.handler, xml.sax.saxutils

import snap

class Package:
    """information about a package tracked by snap"""

    def __init__(self, name='', version=''):
        '''initialize the package

        @param name - the name of the package
        @param version - version of the package, currently not used
        '''

        self.name = name
        self.version = version

class PackagesRecordFile:
    '''a snap package record file, contains list of packages installed, to restore'''
    
    def __init__(self, filename):
        '''initialize the file

        @param filename - path to the file 
        '''

        self.packagefile = filename

    def write(self, packages):
        '''generate file containing record of packages

        @param packages - list of Packages to record
        '''
        f=open(self.packagefile, 'w')
        f.write("<packages>")
        for package in packages:
            f.write('<package>' + xml.sax.saxutils.escape(package.name) + '</package>');
        f.write("</packages>")
        f.close()

    def read(self):
        '''
        read packages from the file

        @returns - list of instances of Package
        '''
        parser = xml.sax.make_parser()
        parser.setFeature(xml.sax.handler.feature_namespaces, 0)
        handler = _PackagesRecordFileParser()
        parser.setContentHandler(handler)
        parser.parse(self.packagefile)
        return handler.packages
        


class _PackagesRecordFileParser(xml.sax.handler.ContentHandler):
    '''internal class to parse the packages record file xml'''

    def __init__(self):
        # list of packages parsed
        self.packages = []

        # current package being processed
        self.current_package=None

        # flag indicating if we are evaluating a name
        self.in_package_content=False
    
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
            self.packages.append(Package(name=xml.sax.saxutils.unescape(self.current_package)))
