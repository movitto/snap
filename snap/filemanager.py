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
import shutil
import snap.exceptions

class FileManager:
    """Snap file manager, performs many high level file operations"""

    def rm(target):
        '''remove the specified file - static method

        @param target - the path to the file to remove
        @raises FileSystemError - if the file could not be removed'''
        try:
            os.remove(target)
        except:
            raise snap.exceptions.FilesystemError("Could not remove file " + target)
    rm = staticmethod(rm)

    def mv(source, dest):
        '''move specified source file to dest

        @param source - path to the file to move
        @param dest - path to the location to move the file to'''
        try:
            shutil.move(source, dest)
        except:
            raise snap.exceptions.FilesystemError("Could not move the file " + source + " to " + dest)
    mv = staticmethod(mv)

    def make_dir(target):
        '''create the specified directory - static method

        @param target - the path to the directory to create
        @raises FileSystemError - if the directory could not be created
        '''

        try:
            if not os.path.isdir(target):
                os.mkdir(target)
        except:
            raise snap.exceptions.FilesystemError("Could not make directory " + target)
    make_dir = staticmethod(make_dir)

    def rm_dir(target):
        '''remove the specified directory - static method

        @param target - the path to the directory to remove
        @raises FileSystemError - if the directory could not be removed
        '''

        try:
            if os.path.isdir(target):
                shutil.rmtree(target)
        except:
            raise snap.exceptions.FilesystemError("Could not remove directory " + target)
    rm_dir = staticmethod(rm_dir)


    def exists(path):
        '''return true if the file specified by the given path exists, else false

        @param path - path to th file to check
        @return - true if the file exists, else false'''
        
        return os.path.exists(path)
    exists = staticmethod(exists)

    def read_file(path):
        '''return and return the entire contents of the specified file

        @param path - path to th file to check
        @return - contents of the file exists'''

        try:
            f = open(path, 'r')
            c = f.read()
            f.close()
            return c
        except:
            raise snap.exceptions.FilesystemError("Could not read file " + path)
    read_file = staticmethod(read_file)

    def get_all_files(include_dirs=[], exclude_dirs=[]):
        '''return a list of paths corresponding to files in one or more directories - static method

        @param include_dirs - list of directories to start in
        @param exclude_dirs - list of directories to exclude'''
        if len(include_dirs) == 0:
            include_dirs.append(snap.osregistry.OS.get_root())
        
        files = []
        # iterate over each directory in the include list
        for directory in include_dirs:
            try:
                for name in os.listdir(directory):
                    fullpath = os.path.join(directory, name)
                    # add all files in the directory
                    if os.path.isfile(fullpath) and not fullpath in files:
                        files.append(fullpath)
    
                # iterate over all subdirectories
                subdirs = FileManager.get_all_subdirectories(directory)
                for subdirectory in subdirs:
                    fullpath = os.path.join(directory, subdirectory)
                    # exclude those in the exclude list
                    if not fullpath in exclude_dirs:
                        subdir_files = FileManager.get_all_files([fullpath], exclude_dirs)
                        # add all files in the subdirectory
                        for subdir_file in subdir_files:
                            if not subdir_file in files:
                                files.append(subdir_file)
            except:
                pass # silently ignore errors
        return files
    get_all_files = staticmethod(get_all_files)

    def get_all_subdirectories(directory=None, recursive=False):
        '''return a list of full paths to subdirectories under the specified directory
        
        @param directory - the directory to get subdirectories of
        '''
        if directory == None:
            directory = snap.osregistry.OS.get_root()
        
        subdirs = []
        # iterate over all files in directory
        for item in os.listdir(directory):
            fullpath = os.path.join(directory, item)
            # get subdirectories
            if os.path.isdir(fullpath) and not fullpath in subdirs:
                subdirs.append(fullpath)
                # recusrively iterate over subdirectories
                if recursive:
                    subsubdirs = FileManager.get_all_subdirectories(fullpath)
                    for subsubdir in subsubdirs:
                        if not subsubdir in subdirs:
                            subdirs.append(subsubdir)
        return subdirs
    get_all_subdirectories = staticmethod(get_all_subdirectories)
