#!/usr/bin/python
#
# Metadata pertaining to files backed up / restored by Snap!
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

import os
import shutil

from snap.filemanager import FileManager

class SFile(object):
    """A generic file tracked by snap"""

    path=''
    name=''
    directory=''

    def __init__(self, path=''):
        '''initialize the generic file

        @param path - the path to the file
        '''

        self.path = path

        path_components = path.split('/')
        self.name = path_components[len(path_components)-1]

        path_components.pop()
        self.directory = '/'.join(*path_components)

    def copy_to(basedir, path_prefix=''):
        '''copy the sfile to the specified base directory, replicating the directory structure
           of the path under it
           
           @param basedir - the directory to replicate the path and copy the file to
           @param path_prefix - an optional prefix to prepend to the sfile path'''
        os.makedirs(basedir + self.directory)
        shutil.copystat(self.directory, basedir + self.directory)
        ofs = os.stat(self.directory)
        os.chown(basedir + self.directory, ofs.st_uid, ofs.st_gid)

        shutil.copyfile(path_prefix + self.path, basedir + self.path)
        shutil.copystat(path_prefix + self.path, basedir + self.path)
        ofs = os.stat(path_prefix + sfile.path)
        os.chown(basedir + self.path, ofs.st_uid, ofs.st_gid)

class FilesRecordFile:
    '''a snap files record file, contains list of files modified, to restore'''
    
    def __init__(self, recordfile)
       self.recordfile = recordfile

    def write(self, sfiles=[]):
       '''generate file containing record of specified files

       @param files - the list of SFiles to record
       '''
       f=open(self.recordfile, 'w') 
       f.write('<files>\n')
       for sfile in files:
           f.write(' <file>\n  ' + saxutils.escape(sfile.path) + '\n </file>\n')
       f.write('</files>\n')
       f.close()

    def read(self):
       '''restore the files stored in and tracked by the record file in the targetdir'''
       parser = xml.sax.handler.make_parser()
       parser.setFeature(xml.sax.handler.feature_namespaces, 0)
       handler = _FilesRecordFileParser()
       parser.setContentHandler(handler)
       parser.parse(self.recordfile)
       return handler.files

# internal class to parse the record file
class _FilesRecordFileParser(handler.ContentHandler):
    # list of files parsed
    files = []

    # current data being processed
    current_path=None

    # if we are currently evaluating a file
    in_file_content=False

    def startElement(self, name, attrs):
        if name == 'file':
            self.current_path = ''
            self.in_file_content=True

    def characters(self, ch):
        if self.in_file_content:
            if ch != '\n':
                self.current_path = self.current_path + ch


    def endElement(self, name):
        if name == 'file':
            self.in_file_content = False
            files.append(SFile(saxutils.unescape(self.current_path)))
