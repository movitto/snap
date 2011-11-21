#!/usr/bin/python
#
# Methods to backup/restore files on windows, implementing snap.SnapshotTarget
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
import tempfile
import subprocess

import snap
from snap.osregistry import OSUtils
from snap.filemanager    import FileManager
from snap.metadata.sfile import SFile, FilesRecordFile

class Win(snap.snapshottarget.SnapshotTarget):
    '''implements the snap! files target backend on windows'''

    # for now just record a static list of directories to exclude from backup
    EXCLUDE_DIRS = ["C:\\Program Files", "C:\\Program Files(x86)", "C:\\Windows"]

    def __init__(self):
        self.fs_root = ''

    def backup(self, basedir, include=[], exclude=[]):
        """backup the files modified outside the apt package system"""

        if snap.config.options.log_level_at_least('verbose'):
            snap.callback.snapcallback.message("Backing up files on windows")

        # get list of hard drives
        if len(include) == 0:
            drives = []
            null = open(OSUtils.null_file(), "w")
            tfile = tempfile.TemporaryFile()
            popen = subprocess.Popen(["fsutil", "fsinfo", "drives"], stdout=tfile, stderr=null)
            popen.wait()
            tfile.seek(0)
            c = tfile.read()
            
            drives = c.split()[1:]
       
            # loop through each drive and determine which are available
            for drive in drives:
                include_drive = True
                try:
                    os.listdir(drive)
                except WindowsError, e:
                    include_drive = False
                if include_drive:
                    include.append(drive)

        # else apply path manipulation to specified includes
        else:
            for i in range(len(include)):
                include[i] = SFile.windows_path_escape(include[i])

        for additional_exclude in Win.EXCLUDE_DIRS:
            if not additional_exclude in exclude:
                exclude.append(additional_exclude)

        # remove duplicates
        include = list(set(include))
        exclude = list(set(exclude))

        # determine which files have been modified since installation
        #   and copy those to basedir
        sfiles = []
        files = FileManager.get_all_files(include, exclude)
        for tfile in files:
            if snap.config.options.log_level_at_least('verbose'):
                snap.callback.snapcallback.message("Backing up file " + tfile);
            try:
                sfile = SFile(tfile)
                sfile.copy_to(basedir)
                sfiles.append(sfile)
            except:
                pass

        # write record file to basedir
        record = FilesRecordFile(os.path.join(basedir, "files.xml"))
        record.write(sfiles)


    def restore(self, basedir):
        """restore the files in the snapfile"""
        # if files record file isn't found, simply return
        if not os.path.isfile(os.path.join(basedir, "files.xml")):
            return

        if snap.config.options.log_level_at_least('verbose'):
            snap.callback.snapcallback.message("Restoring files on windows");

        # read files from the record file
        record = FilesRecordFile(os.path.join(basedir, "files.xml"))
        sfiles = record.read()

        # restore those to their original locations
        for sfile in sfiles:
            if snap.config.options.log_level_at_least('verbose'):
                snap.callback.snapcallback.message("Restoring file " + sfile.path);
            try:
                sfile.copy_to(self.fs_root, basedir)
            except:
                if snap.config.options.log_level_at_least('normal'):
                    snap.callback.snapcallback.message("Failed to restore file " + sfile.path);
            
