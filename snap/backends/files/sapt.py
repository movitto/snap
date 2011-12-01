# Methods to backup/restore files using apt, implementing snap.SnapshotTarget
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
import apt

import snap
from snap.filemanager    import FileManager
from snap.metadata.sfile import SFile, FilesRecordFile

class Sapt(snap.snapshottarget.SnapshotTarget):
    '''implements the snap! files target backend using the apt package system'''

    def __init__(self):
        self.fs_root='/'

        self.cache = apt.Cache()
        self.cache.update()
        self.cache.open(None)

        # build index of installed files -> packages that provide them
        self.installed_file_packages = {}
        for pkg in self.cache:
            if pkg.is_installed:
                for pfile in pkg.installed_files:
                    self.installed_file_packages[pfile] = pkg

    def __file_modified(self,file_name):
        '''return true if package has been modified since installation, else false'''

        # if the file isn't tracked by the package system
        if not file_name in self.installed_file_packages:
            return True

        pkg = self.installed_file_packages[file_name] 


        modified_time = os.stat(file_name).st_mtime

        # seems that comparing the modified_time against this time is the only way togo
        # http://lists.netisland.net/archives/plug/plug-2008-02/msg00205.html
        pkg_modified_time = os.stat('/var/lib/dpkg/info/' + pkg.name + '.list').st_mtime
        
        if modified_time > pkg_modified_time:
            return True

        # finally if the file is a deb conffile, we just assume its modified since
        # there is no way to determine if the file was modified before the package
        # was updated (see the link above)
        conf_file='/var/lib/dpkg/info/' + pkg.name + '.conffiles'
        if os.path.isfile(conf_file):
            c = FileManager.read_file(conf_file)
            if len(re.findall(file_name, c)) > 0:
                return True

        return False

    def backup(self, basedir, include=[], exclude=[]):
        """backup the files modified outside the apt package system"""

        if snap.config.options.log_level_at_least('verbose'):
            snap.callback.snapcallback.message("Backing up files using apt backend");

        if len(include) == 0:
            include = ['/']

        for additional_exclude in ['/proc', '/sys', '/selinux']:
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
            if self.__file_modified(tfile):
                if snap.config.options.log_level_at_least('verbose'):
                    snap.callback.snapcallback.message("Backing up file " + tfile);
                sfile = SFile(tfile)
                sfile.copy_to(basedir)
                sfiles.append(sfile)

        # write record file to basedir
        record = FilesRecordFile(basedir + "/files.xml")
        record.write(sfiles)


    def restore(self, basedir):
        """restore the files in the snapfile"""
        # if files record file isn't found, simply return
        if not os.path.isfile(basedir + "/files.xml"):
            return

        if snap.config.options.log_level_at_least('verbose'):
            snap.callback.snapcallback.message("Restoring files using apt backend");

        # read files from the record file
        record = FilesRecordFile(basedir + "/files.xml")
        sfiles = record.read()

        # restore those to their original locations
        for sfile in sfiles:
            if snap.config.options.log_level_at_least('verbose'):
                snap.callback.snapcallback.message("Restoring file " + sfile.path);
            sfile.copy_to(self.fs_root, basedir)
