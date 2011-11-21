#!/usr/bin/python
#
# Methods to backup/restore software on windows, implementing snap.SnapshotTarget.
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

import re
import os
import tempfile
import subprocess

import snap
from snap.osregistry import OSUtils
from snap.metadata.sfile import SFile
from snap.filemanager import FileManager
from snap.metadata.package import Package, PackagesRecordFile

class Win(snap.snapshottarget.SnapshotTarget):
    '''implements the snap! packages target backend on windows'''

    def get_packages():
        # retrieve list of installed software
        null = open(OSUtils.null_file(), "w")
        tfile = tempfile.TemporaryFile()
        popen = subprocess.Popen(["reg", "query", "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall", "/s"],
                                 stdout=tfile, stderr=null)
        popen.wait()

        tfile.seek(0)
        c = tfile.read()
        tfile.close()

        # parse install locations out of this
        packages = []
        for match in re.finditer(r"InstallLocation\s*REG_SZ[ \t]*([a-zA-Z][^\n]+)\r\n", c):
            install_location = match.group(1)
            packages.append(Package(install_location))

        return packages
    get_packages = staticmethod(get_packages)

    def __init__(self):
        pass

    def backup(self, basedir, include=[], exclude=[]):
        '''backup the packages installed locally'''
        if snap.config.options.log_level_at_least('verbose'):
            snap.callback.snapcallback.message("Backing up software on windows");

        packages = Win.get_packages()

        # backup program files
        for pkg in packages:
            for pkg_file in FileManager.get_all_files(include_dirs=[pkg.name]):
                SFile(pkg_file).copy_to(os.path.join(basedir, "windows-packages"))

        # TODO Backup registry?

        # write record file to basedir
        record = PackagesRecordFile(os.path.join(basedir, "packages.xml"))
        record.write(packages)

    def restore(self, basedir):
        '''restore the packages from the snapfile'''
        # if package record file isn't found, simply return
        if not os.path.isfile(os.path.join(basedir, "packages.xml")):
            return

        if snap.config.options.log_level_at_least('verbose'):
            snap.callback.snapcallback.message("Restoring software on windows");

        # read files from the record file
        record = PackagesRecordFile(os.path.join(basedir, "packages.xml"))
        packages = record.read()

        # TODO restore registry?

        # restore program files
        for pkg_file in FileManager.get_all_files(include_dirs=[os.path.join(basedir, "windows-packages")]):
            partial_path = pkg_file.replace(os.path.join(basedir, "windows-packages") + "\\", "")
            try:
                SFile(partial_path).copy_to(path_prefix=os.path.join(basedir, "windows-packages"))
            except:
                if snap.config.options.log_level_at_least('normal'):
                    snap.callback.snapcallback.message("Failed to restore windows package file " + partial_path);
