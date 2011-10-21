#!/usr/bin/python
#
# High level file manager / helper
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
import snap.exceptions

class FileManager:
    """Snap file manager, performs many high level file operations"""

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

    def rm(target):
        '''remove the specified file - static method

        @param target - the path to the file to remove
        @raises FileSystemError - if the file could not be removed'''
        try:
            os.remove(target)
        except:
            raise snap.exceptions.FilesystemError("Could not remove file " + target)
    rm = staticmethod(rm)

    def make_dir(target):
        '''create the specified directory - static method

        @param target - the path to the directory to create
        @raises FileSystemError - if the directory could not be created
        '''

        try:
            os.mkdir(target)
        except:
            raise snap.exceptions.FilesystemError("Could not make directory " + target)
    make_dir = staticmethod(make_dir)

    def exists(path):
        '''return true if the file specified by the given path exists, else false

        @param path - path to th file to check
        @return - true if the file exists, else false'''
        
        return os.path.exists(path)
    exists = staticmethod(exists)

    def get_all_files(include_dirs=['/'], exclude_dirs=[]):
        '''return a list of paths corresponding to files in one or more directories - static method

        @param include_dirs - list of directories to start in
        @param exclude_dirs - list of directories to exclude'''
        files = []
        # iterate over each directory in the include list
        for directory in include_dirs:
            for name in os.listdir(directory):
                fullpath = os.path.join(directory, name)
                # add all files in the directory
                if os.path.isfile(fullpath) and not os.path.islink(fullpath) and
                   not fullpath in files:
                       files.append(fullpath)

            # iterate over all subdirectories
            subdirs = get_all_subdirectories(directory)
            for subdirectory in subdirs:
                fullpath = os.path.join(directory, subdirectory)
                # exclude those in the exclude list
                if not os.path.islink(fullpath) and not fullpath in exclude_dirs:
                    subdir_files = get_all_files([fullpath], exclude_dirs)
                    # add all files in the subdirectory
                    for subdir_file in subdir_files:
                        if not subdir_file in files:
                            files.append(subdir_file)
         return files
    get_all_files = staticmethod(get_all_files)

    def get_all_subdirectories(directory='/', recursive = False):
        '''return a list of full paths to subdirectories under the specified directory
        
        @param directory - the directory to get subdirectories of
        '''
        subdirs = []
        # iterate over all files in directory
        for item in os.listdir(directory)
            fullpath = os.path.join(dirs[i],name)
            # get subdirectories
            if os.path.isdir(fullpath) and not os.path.islink(fullpath) and
               not fullpath in subdirs:
                   subdirs.append(fullpath)
                   # recusrively iterate over subdirectories
                   if recursive:
                       subsubdirs = get_all_subdirectories(fullpath)
                       for subsubdir in subsubdirs:
                           if not subsubdir in subdirs:
                               subdirs.append(subsubdir)
         return subdirs
    get_all_sub_directories = staticmethod(get_all_sub_directories)
