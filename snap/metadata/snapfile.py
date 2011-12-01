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

# skip snapshot encyrption support on windows for the time being
if not snap.osregistry.OS.is_windows():
    from snap.crypto      import Crypto

class SnapFile:
    """The snapfile, the end result of the backup operation
       and input into the restore operation. This is a tar guziped archive."""

    def __init__(self, snapfile, snapdirectory, encryption_password=None):
        '''initialize the snapfile

        @param snapfile - the path to the snapfile to create / read
        @param snapdirectory - the path to the directory to compress/extract
        @param encryption_password - the password to use in the encryption/decryption operations, if set to None encryption will be disabled
        @raises - MissingDirError - if the snapdirectory is invalid
        '''
        if not os.path.isdir(snapdirectory):
            raise MissingDirError(snapdirectory + " is an invalid snap working directory ")
        self.snapfile = snapfile
        self.snapdirectory = snapdirectory
        self.encryption_password = encryption_password

        if  not snap.osregistry.OS.is_windows() and self.encryption_password != None:
            self.encryption_key = Crypto.generate_key(self.encryption_password)
        else:
            self.encryption_key = None

    def __prepare_file_for_tarball(tarball, fullpath, partialpath):
        '''set attributes of a file for inclusion in a tarball'''
        fs = os.stat(fullpath)
        tarinfo = tarball.gettarinfo(partialpath)
        tarinfo.name = partialpath
        tarinfo.uid = fs.st_uid
        tarinfo.gid = fs.st_gid
        tarinfo.mtime = fs.st_mtime
        tarinfo.mode = fs.st_mode
        return tarinfo
    __prepare_file_for_tarball = staticmethod(__prepare_file_for_tarball)
        
    def compress(self):
        '''create a snapfile from the snapdirectory

        @raises - MissingFileError - if the snapfile cannot be created
        '''
        # create the tarball
        tarball = tarfile.open(self.snapfile, "w:gz")

        # temp store the working directory, before changing to the snapdirectory
        cwd = os.getcwd()
        os.chdir(self.snapdirectory)
        
        seperator = snap.osregistry.OS.get_path_seperator()

        # copy directories into snapfile
        for sdir in FileManager.get_all_subdirectories(os.getcwd(), recursive=True):
            partialpath = sdir.replace(self.snapdirectory + seperator, "")
            tarball.addfile(self.__prepare_file_for_tarball(tarball, sdir, partialpath))

        # copy files into snapfile
        for tfile in FileManager.get_all_files(include_dirs=[os.getcwd()]):
            partialpath = tfile.replace(self.snapdirectory + seperator, "")
            tarball.addfile(self.__prepare_file_for_tarball(tarball, tfile, partialpath), file(tfile, 'rb'))

        # finish up tarball creation
        tarball.close()

        # encrypt the snapshot if we've set a key
        if not snap.osregistry.OS.is_windows() and self.encryption_key != None:
            if snap.config.options.log_level_at_least('verbose'):
                snap.callback.snapcallback.message("Encyrpting snapfile")
            Crypto.encrypt_file(self.encryption_key, self.snapfile, self.snapfile + ".enc")
            FileManager.mv(self.snapfile + ".enc", self.snapfile)

        if snap.config.options.log_level_at_least('normal'):
            snap.callback.snapcallback.message("Snapfile " + self.snapfile + " created")

        # restore the working directory
        os.chdir(cwd)

    def extract(self):
        '''extract the snapfile into the snapdirectory
        
        @raises - MissingFileError if the snapfile does not exist
        '''

        # decrypt the file if we've set a key
        if not snap.osregistry.OS.is_windows() and self.encryption_key != None:
            if snap.config.options.log_level_at_least('verbose'):
                snap.callback.snapcallback.message("Decyrpting snapfile")
            Crypto.decrypt_file(self.encryption_key, self.snapfile, self.snapfile + ".dec")
            FileManager.mv(self.snapfile + ".dec", self.snapfile)

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
            snap.callback.snapcallback.message("Snapfile " + self.snapfile + " opened")

        # restore the working directory
        os.chdir(cwd)
