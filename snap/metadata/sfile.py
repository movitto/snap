#!/usr/bin/python
#
# Metadata pertaining to files backed up / restored by Snap!
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
import re
import shutil
import xml, xml.sax, xml.sax.handler, xml.sax.saxutils

import snap.osregistry
from snap.filemanager import FileManager

class SFile(object):
    """A generic file tracked by snap"""

    def windows_path_escape(path):
        '''helper to handle drive specifications in windows paths'''
        # XXX total dirty hack
        m = re.search("^([^:]*):\\\\(.*)", path)
        if m:
            return m.group(1) + "___" + m.group(2)
        else:
            m = re.search("^([^_]*)___(.*)", path)
            if m:
                return m.group(1) + ":\\" + m.group(2)
        return path
    windows_path_escape = staticmethod(windows_path_escape)

    def __init__(self, path=''):
        '''initialize the generic file

        @param path - the path to the file
        '''

        self.path = path

        self.directory, self.name = os.path.split(self.path)

    def copy_to(self, basedir='', path_prefix=''):
        '''copy the sfile to the specified base directory, replicating the directory structure
           of the path under it
           
           @param basedir - the directory to replicate the path and copy the file to
           @param path_prefix - an optional prefix to prepend to the sfile path'''
        source_path = os.path.join(path_prefix, self.path)
        source_dir = os.path.join(path_prefix, self.directory)
        
        # XXX need to incorporate a bit of a hack to handle the
        #  drive specification in windows paths
        if snap.osregistry.OS.is_windows():
            self.path = SFile.windows_path_escape(self.path)

        dest_path = os.path.join(basedir, self.path)
        dest_dir, dest_name = os.path.split(self.path)
        dest_dir = os.path.join(basedir, dest_dir)

        if not os.path.isdir(dest_dir):
            os.makedirs(dest_dir)
            shutil.copystat(source_dir, dest_dir)
            ofs = os.stat(source_dir)
            snap.osregistry.OSUtils.chown(dest_dir, uid=ofs.st_uid, gid=ofs.st_gid)

        if os.path.islink(source_path):
            if os.path.isfile(dest_path):
                os.remove(dest_path)
            realpath = os.path.realpath(source_path)
            os.symlink(realpath, dest_path)

        elif os.path.isfile(source_path):
            shutil.copyfile(source_path, dest_path)
            shutil.copystat(source_path, dest_path)
            ofs = os.stat(source_path)
            snap.osregistry.OSUtils.chown(dest_path, uid=ofs.st_uid, gid=ofs.st_gid)

class FilesRecordFile:
    '''a snap files record file, contains list of files modified, to restore'''
    
    def __init__(self, recordfile):
       self.recordfile = recordfile

    def write(self, sfiles=[]):
       '''generate file containing record of specified files

       @param files - the list of SFiles to record
       '''
       f = open(self.recordfile, 'w') 
       f.write('<files>')
       for sfile in sfiles:
           f.write('<file>' + xml.sax.saxutils.escape(sfile.path) + '</file>')
       f.write('</files>')
       f.close()

    def read(self):
       '''restore the files stored in and tracked by the record file in the targetdir'''
       parser = xml.sax.make_parser()
       parser.setFeature(xml.sax.handler.feature_namespaces, 0)
       handler = _FilesRecordFileParser()
       parser.setContentHandler(handler)
       parser.parse(self.recordfile)
       return handler.files

class _FilesRecordFileParser(xml.sax.handler.ContentHandler):
    '''internal class to parse the files record file'''

    def __init__(self):
        # list of files parsed
        self.files = []

        # current data being processed
        self.current_path = None

        # if we are currently evaluating a file
        self.in_file_content = False

    def startElement(self, name, attrs):
        if name == 'file':
            self.current_path = ''
            self.in_file_content = True

    def characters(self, ch):
        if self.in_file_content:
            if ch != '\n':
                self.current_path = self.current_path + ch


    def endElement(self, name):
        if name == 'file':
            self.in_file_content = False
            self.files.append(SFile(xml.sax.saxutils.unescape(self.current_path)))
