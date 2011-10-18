#!/usr/bin/python
#
# snap file system operations and manager
# snap file formats including generic files,
#  'snap record file', and the snapfile 
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

import os
import shutil

from xml.sax import make_parser
from xml.sax import handler,saxutils
from xml.sax.handler import feature_namespaces

import snap, snap.callback
from snap.snapoptions import debug,FS_FAILSAFE
from snap.exceptions import *

class SFile(object):
    """A generic file tracked by snap"""

    name=''
    currentpath=''
    status=None # as returned by packagesyste.get_file_status
    def __init__(self, name='', currentpath='', status=None):
        '''initialize the generic file

        @param name - the name of the file
        @param currentpath - the path to the file
        @param status - boolean indicating if it was installed by a package system
                        and if so, if it has been modified since installation
        '''

        self.name = name
        self.currentpath = currentpath
        self.status = status

class FileManager:
    """Snap file manager, performs many high level file operations with respect
       to snapoptions.FS_FAILSAFE which provides a failsafe for all filesystem
       operations"""

    # name of the file which to store records 
    recordfile=None

    # directory which to copy/read files 
    targetdirectory=None

    def __init__(self, recordfile=None, targetdirectory=None):
        '''initialize the file manager

        @param recordfile - optional snap record file which to read/write
        @param tagetdirectory - temporary directory which to read/write files
        '''

        self.recordfile = recordfile
        self.targetdirectory = targetdirectory

    def make_dir(target):
        '''create the specified directory - static method

        @param target - the path to the directory to create
        @raises SnapFileSystemError - if the directory could not be created
        '''

        try:
            os.mkdir(target)
        except:
            snap.callback.snapcallback.error("Could not make directory " + target)
            raise SnapFilesystemError
    make_dir = staticmethod(make_dir)

    def get_file(path):
        '''create and return a SFile for the file on the given path - static method

        @param path - path to input file
        @return - the corresponding SFile
        '''

        name = path.split('/')
        return SFile(name[len(name) - 1], path)
    get_file = staticmethod(get_file)

    def get_all_files(startingDirs='/', excludingDirs='', psa=None):
        '''return a list of SFile's corresponding to files in one or more directories - static method

        @param startingDirs - colon seperated list of directories to start in
        @param excludingDirs - optional colon seperated list directories to exlclude
        @param psa - optional package system adaptor to lookup file info
        '''

        files = []
        startDirs = startingDirs.split(':')
        excludeDirs = excludingDirs.split(':')
        while len(startDirs)>0:
            directory = startDirs.pop()
            try:
                excludeDirs.index(directory)
            except: # the current directory is not in the excluded directory list
                try:
                   for name in os.listdir(directory):
                      fullpath = os.path.join(directory,name)
                      if os.path.isfile(fullpath) and not os.path.islink(fullpath):
                         status = None
                         if psa != None:
                            status = psa.get_file_status(fullpath)
                         files.append(SFile(name, fullpath, status))
                      elif os.path.isdir(fullpath) and not os.path.islink(fullpath):
                          startDirs.append(fullpath)  # It's a directory, store it.
                except:
                    None
        return files  
    get_all_files = staticmethod(get_all_files)

    def get_all_sub_directories(startingDir='/'):
        '''return a list of full paths to subdirectories under the specified directory
        
        @param startingDir - the directory to start in
        '''
        dirs  = [startingDir]
        i = 0
        while i != len(dirs):
            for name in os.listdir(dirs[i]):
                fullpath = os.path.join(dirs[i],name)
                if os.path.isdir(fullpath) and not os.path.islink(fullpath):
                    dirs.append(fullpath)
            i += 1
        dirs.pop(0) # specified dir isn't a subdir of itself
        return dirs
    get_all_sub_directories = staticmethod(get_all_sub_directories)

    def copy_file(file, destdir, includedirs=False):
        '''copy a file from source to destination - static method
           
           @param file - the SFile to copy
           @param destdir - destination directory to copy file to
           @param includedirs - set true to recursively make dirs under destdir correspond to path in file
        '''
        if not os.path.exists(destdir):
            os.mkdir(destdir)
        destdir += '/'
        tpath = ""
        if includedirs:
            pathcomponents = file.currentpath.split('/')
            for i,path in enumerate(pathcomponents):
                if (i+1) != len(pathcomponents):
                    tpath += path + '/'
                    if not os.path.exists(destdir + tpath):
                        os.mkdir(destdir + tpath)
                        shutil.copystat(tpath, destdir + tpath)
                        ofs = os.stat(tpath)
                        os.chown(destdir + tpath, ofs.st_uid, ofs.st_gid)
        debug(" copying " + file.currentpath + " to " + destdir + tpath + file.name)
        if not FS_FAILSAFE:
            shutil.copyfile(file.currentpath, destdir + tpath + file.name)
            shutil.copystat(file.currentpath, destdir + tpath + file.name)# perserve permissions/access&mod times
            ofs = os.stat(file.currentpath)
            os.chown(destdir + tpath + file.name, ofs.st_uid, ofs.st_gid) # perserve file owner/group
    copy_file = staticmethod(copy_file)

    def backup(self, files):
       '''backup the list of files into targetdirectory and create a record file

       @param files - the list of SFiles to backup
       '''

       snap.callback.snapcallback.backup_files()
       f=open(self.recordfile, 'w') 
       f.write('<files>\n')
       tdir = self.targetdirectory
       for fle in files:
            if fle.status: # new/modified status check here
                try:
                    snap.callback.snapcallback.backup_file(fle)
                    self.copy_file(fle, self.targetdirectory, True)
                    f.write(' <file>\n' + saxutils.escape(fle.currentpath) + '\n </file>\n')
                except:
                    snap.callback.snapcallback.warn(' Failure backing up ' + fle.name)
                    debug('Failure backing up ' + fle.name)
       f.write('</files>\n')
       f.close()

    def restore(self):
       '''restore the files stored in and tracked by the record file in the targetdir'''

       snap.callback.snapcallback.restore_files()
       files=[]
       parser = make_parser()
       parser.setFeature(feature_namespaces, 0)
       dh = _RecordFileParser(files, self.targetdirectory)
       parser.setContentHandler(dh)
       parser.parse(self.recordfile)
       return files
       
# internal class to parse the record file
#class _RecordFileParser(saxutils.DefaultHandler):
class _RecordFileParser(handler.ContentHandler):
    # list of files parsed
    files = None

    # base path which to copy files from
    bashpath = None

    # current file being processed
    currentfile=None

    # if we are currently evaluating a file
    inFileContent=False

    def __init__(self, files, basepath):
        self.files = files
        self.basepath = basepath

    def startElement(self, name, attrs):
        if name == 'file':
            self.currentfile = SFile()
            self.files.append(self.currentfile)
            self.inFileContent=True

    def characters(self, ch):
        if self.inFileContent:
            if ch != '\n':
                self.currentfile.currentpath = self.currentfile.currentpath + ch


    def endElement(self, name):
        if name == 'file':
            self.inFileContent = False
            try:
                self.currentfile.currentpath = saxutils.unescape(self.currentfile.currentpath)
                self.currentfile.name = self.currentfile.currentpath.split('/').pop().rstrip()
                os.chdir(self.basepath)
                self.currentfile.currentpath =  '.' + self.currentfile.currentpath.rstrip()
                snap.callback.snapcallback.restore_file(self.currentfile)
                FileManager.copy_file(self.currentfile, '/', True)
            except:
                snap.callback.snapcallback.warn(" Failed restoring " + self.currentfile.currentpath)
                debug(" Failed restoring " + self.currentfile.currentpath)


import tarfile
class SnapFile:
    """The snapfile, the end result of the backup operation
       and input into the restore operation. This is a tar guziped archive."""

    # @param snapfile tarball
    # @param snapdirectory directory which to read/write files
    def __init__(self, snapfile, snapdirectory):
        '''initialize the snapfile

        @param snapfile - the path to the snapfile to create / read
        @param snapdirectory - the path to the directory to compress/extract
        @raises - SnapMissingDirError - if the snapdirectory is invalid
        '''

        if not os.path.isdir(snapdirectory):
            snap.callback.snapcallback.error(" " + snapdirectory + " is an invalid snap working directory ")
            raise SnapMissingDirError()
        self.snapfile = snapfile
        self.snapdirectory = snapdirectory
        
    def compress(self):
        '''create a snapfile from the snapdirectory

        @raises - SnapMissingFileError - if the snapfile cannot be created
        '''
        def handle_file(tarball, fullpath, handle):
            fs = os.stat(fullpath)
            tarinfo = tarball.gettarinfo(handle)
            tarinfo.uid = fs.st_uid
            tarinfo.gid = fs.st_gid
            tarinfo.mtime = fs.st_mtime
            tarinfo.mode = fs.st_mode
            return tarinfo


        if (os.path.isfile(self.snapfile) and not os.access(self.snapfile, os.W_OK)) or (not os.path.exists(self.snapfile) and not os.access(self.snapfile.rpartition('/')[0], os.W_OK)):  # check if file is writable or creatable
            snap.callback.snapcallback.error(" " + self.snapfile + " is an invalid snapfile ") 
            raise SnapMissingFileError()
        os.chdir(self.snapdirectory)
        tarball = tarfile.open(self.snapfile, "w:gz")
        for dir in FileManager.get_all_sub_directories(self.snapdirectory):
            handle = dir.replace(self.snapdirectory + "/", "")
            tarball.addfile(handle_file(tarball, dir, handle))
        #    handle_file(tarball, dir, dir.replace(self.snapdirectory + "/", ""))
        for fle in FileManager.get_all_files(self.snapdirectory):
            handle = fle.currentpath.replace(self.snapdirectory + "/", "")
            tarball.addfile(handle_file(tarball, fle.currentpath, handle), file(handle))
        tarball.close()
        snap.callback.snapcallback.snapfile_created(self)

    def extract(self):
        '''extract the snapfile into the snapdirectory
        
        @raises - SnapMissingFileError if the snapfile does not exist
        '''

        if not os.path.isfile(self.snapfile) or not os.access(self.snapfile, os.R_OK):
            snap.callback.snapcallback.error(" " + self.snapfile + " is an invalid snapfile ")
            raise SnapMissingFileError()
        os.chdir(self.snapdirectory)
        tarball = tarfile.open(self.snapfile) 
        for tarinfo in tarball:
            tarball.extract(tarinfo)
        tarball.close()
        snap.callback.snapcallback.snapfile_restored(self)
