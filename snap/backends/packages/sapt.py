#!/usr/bin/python
#
# Methods to backup/restore packages using apt, implementing snap.SnapshotTarget.
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
import apt
import sets

import snap
from snap.metadata.package import Package, PackagesRecordFile

class Syum(snap.snapshottarget.SnapshotTarget):
    '''implements the snap! packages target backend using the apt package system'''

    def __init__(self):
        self.fs_root='/'

        self.cache = apt.Cache()
        self.cache.update()
        self.cache.open(None)

    def backup(self, basedir, include=[], exclude=[]):
        '''backup the packages installed locally'''
        if snap.config.options.log_level_at_least('verbose'):
            snap.callback.snapcallback.message("Backing up packages using apt backend");

        # retrieve installed packages
        packages=[]
        packagenames = set()
        for pkg in self.cache:
            pkg_name = pkg.sourcePackageName 
            if pkg.is_installed and not pkg_name in packagenames:
                if snap.config.options.log_level_at_least('verbose'):
                    snap.callback.snapcallback.message("Backing up package " + pkg_name)
                packagenames.add(pkg_name)
                packages.append(Package(pkg_name, pkg.versions[0].version))

        # write record file to basedir
        record = PackagesRecordFile(basedir + "/packages.xml")
        record.write(packages)

    def restore(self, basedir):
        '''restore the packages from the snapfile'''
        # first update the system
        self.cache.upgrade()

        # read files from the record file
        record = PackagesRecordFile(basedir + "/packages.xml")
        packages = record.read()

        # mark necessary packages for installation
        for pkg in packages:
            if snap.config.options.log_level_at_least('verbose'):
                snap.callback.snapcallback.message("Restoring package " + pkg.name);
            pkg = self.cache[pkg.name]
            if not pkg.is_installed:
                pkg.mark_install()

        # finally perform install
        self.cache.commit()
