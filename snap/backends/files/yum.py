#!/usr/bin/python
#
# Methods to backup/restore files using yum, implementing snap.SnapshotTarget
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

class Yum(snap.Target):
    #def __init__(self):

    def __file_modified(self,file_name):
        '''return true if package has been modified since installation, else false'''

        # Get all packages that provide the file
        pkgs = self.yum.rpmdb.getProvides(file_name)

        # If no package provides it, file has been modified
        if len(pkgs) == 0:
            return True

        modified_time = os.stat(file_name).st_mtime

        # need just one failure
        for pkg in pkgs:
            # if file modification time > buildtime
            if  modified_time > pkg.hdr["buildtime"]:
                return True

        return False

    def backup(self, basedir, include=['/'], exclude=[]):
        """backup the files modified outside the yum package system"""

        # determine which files have been modified since installation
        #   and copy those to basedir
        sfiles = []
        files = FileManager.get_all_files(include, exclude)
        for tfile in files:
            if self.file_modified(tfile):
                sfile = SFile(tfile)
                sfile.copy_to(basedir)
                sfiles.append(sfile)

        # write record file to basedir
        record = FilesRecordFile(basedir + "files.xml")
        record.write(sfiles)


    def restore(self, basedir):
        """restore the files in the snapfile"""
        # read files from the record file
        record = FilesRecordFile(basedir + "files.xml")
        sfiles = record.read()

        # restore those to their original locations
        for sfile in sfiles:
            sfile.copy_to('/', basedir)
