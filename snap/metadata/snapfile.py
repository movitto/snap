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

import tarfile

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

    def __prepare_file_for_tarball(tarball, fullpath, handle):
        '''set attributes of a file for inclusion in a tarball'''
        fs = os.stat(fullpath)
        tarinfo = tarball.gettarinfo(handle)
        tarinfo.uid = fs.st_uid
        tarinfo.gid = fs.st_gid
        tarinfo.mtime = fs.st_mtime
        tarinfo.mode = fs.st_mode
        return tarinfo
        
    def compress(self):
        '''create a snapfile from the snapdirectory

        @raises - MissingFileError - if the snapfile cannot be created
        '''
        tarball_path = self.snapdirectory + self.snapfile

        # create the tarball
        tarball = tarfile.open(tarball_path, "w:gz")

        # copy directories into snapfile
        for sdir in FileManager.get_all_sub_directories(self.snapdirectory, recursive=True):
            handle = sdir.replace(self.snapdirectory + "/", "")
            tarball.addfile(self.prepare_file_for_tarball(tarball, sdir, handle))

        # copy files into snapfile
        for sfile in FileManager.get_all_files(self.snapdirectory):
            handle = sfile.path.replace(self.snapdirectory + "/", "")
            tarball.addfile(self.prepare_file_for_tarball(tarball, sfile.path, handle), file(handle))

        # finish up tarball creation
        tarball.close()

        if snap.config.options.log_level_at_least('normal'):
            snap.callback.snapcallback.message("Snapfile " + tarball_path + " created")

    def extract(self):
        '''extract the snapfile into the snapdirectory
        
        @raises - MissingFileError if the snapfile does not exist
        '''

        # open the tarball
        tarball = tarfile.open(self.snapfile) 

        # extract files from it
        for tarinfo in tarball:
            tarball.extract(tarinfo)

        # close it out
        tarball.close()

        if snap.config.options.log_level_at_least('normal'):
            snap.callback.snapcallback.message("Snapfile " + tarball_path + " restored")
