#!/usr/bin/python
#
# Metadata pertaining to snapfile, the tarball thats the overall result
#  of the backup operation which gets fed into the restore operation
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
import tarfile

import snap
from snap.filemanager import FileManager
from snap.exceptions  import MissingDirError

class SnapFile:
    """The snapfile, the end result of the backup operation
       and input into the restore operation. This is a tar guziped archive."""

    def __init__(self, snapfile, snapdirectory):
        '''initialize the snapfile

        @param snapfile - the path to the snapfile to create / read
        @param snapdirectory - the path to the directory to compress/extract
        @raises - MissingDirError - if the snapdirectory is invalid
        '''
        if not os.path.isdir(snapdirectory):
            raise MissingDirError(snapdirectory + " is an invalid snap working directory ")
        self.snapfile = snapfile
        self.snapdirectory = snapdirectory

    def __prepare_file_for_tarball(tarball, fullpath):
        '''set attributes of a file for inclusion in a tarball'''
        fs = os.stat(fullpath)
        tarinfo = tarball.gettarinfo(fullpath)
        tarinfo.uid = fs.st_uid
        tarinfo.gid = fs.st_gid
        tarinfo.mtime = fs.st_mtime
        tarinfo.mode = fs.st_mode
        return tarinfo
    __prepare_file_for_tarball=staticmethod(__prepare_file_for_tarball)
        
    def compress(self):
        '''create a snapfile from the snapdirectory

        @raises - MissingFileError - if the snapfile cannot be created
        '''
        # create the tarball
        tarball = tarfile.open(self.snapfile, "w:gz")

        # temp store the working directory, before changing to the snapdirectory
        cwd = os.getcwd()
        os.chdir(self.snapdirectory)

        # copy directories into snapfile
        for sdir in FileManager.get_all_subdirectories(os.getcwd(), recursive=True):
            tarball.addfile(self.__prepare_file_for_tarball(tarball, sdir))

        # copy files into snapfile
        for tfile in FileManager.get_all_files(include_dirs=[os.getcwd()]):
            tarball.addfile(self.__prepare_file_for_tarball(tarball, tfile), file(tfile))

        # finish up tarball creation
        tarball.close()

        if snap.config.options.log_level_at_least('normal'):
            snap.callback.snapcallback.message("Snapfile " + self.snapfile + " created")

        # restore the working directory
        os.chdir(cwd)

    def extract(self):
        '''extract the snapfile into the snapdirectory
        
        @raises - MissingFileError if the snapfile does not exist
        '''

        # open the tarball
        tarball = tarfile.open(self.snapfile) 

        # temp store the working directory, before changing to the snapdirectory
        cwd = os.getcwd()
        os.chdir(self.snapdirectory)

        # extract files from it
        for tarinfo in tarball:
            tarball.extract(tarinfo)

        # close it out
        tarball.close()

        if snap.config.options.log_level_at_least('normal'):
            snap.callback.snapcallback.message("Snapfile " + self.snapfile + " restored")

        # restore the working directory
        os.chdir(cwd)
