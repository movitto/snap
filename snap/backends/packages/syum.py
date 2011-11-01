#!/usr/bin/python
#
# Methods to backup/restore packages using yum, implementing snap.SnapshotTarget.
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
import yum
import sets

import snap
from snap.metadata.package import Package, PackagesRecordFile

class Syum(snap.snapshottarget.SnapshotTarget):
    '''implements the snap! packages target backend using the yum package system'''

    def __init__(self):
        self.yum = yum.YumBase();

        self.fs_root='/'

    def backup(self, basedir, include=[], exclude=[]):
        '''backup the packages installed locally'''
        if snap.config.options.log_level_at_least('verbose'):
            snap.callback.snapcallback.message("Backing up packages using yum backend");

        # retrieve installed packages
        packages=[]
        packagenames = set()
        for pkg in self.yum.rpmdb:
            if not pkg.name in packagenames:
                if snap.config.options.log_level_at_least('verbose'):
                    snap.callback.snapcallback.message("Backing up package " + pkg.name);
                packagenames.add(pkg.name)
                packages.append(Package(pkg.name, pkg.version))

        # write record file to basedir
        record = PackagesRecordFile(basedir + "/packages.xml")
        record.write(packages)

    def restore(self, basedir):
        '''restore the packages from the snapfile'''
        # if package record file isn't found, simply return
        if not os.path.isfile(basedir + "/packages.xml"):
            return

        if snap.config.options.log_level_at_least('verbose'):
            snap.callback.snapcallback.message("Restoring packages using yum backend");

        # set installroot to fs_root
        self.yum.conf.installroot = self.fs_root

        # need this to get around gpgcheck in this case (setting gpgcheck to false will not work)
        self.yum.conf.assumeyes = True

        self.yum.conf.skip_broken = True

        # first update the system
        for pkg in self.yum.rpmdb:
            self.yum.update(pkg)

        # read files from the record file
        record = PackagesRecordFile(basedir + "/packages.xml")
        packages = record.read()

        # grab list of packages
        pl = self.yum.doPackageLists('all')

        # find the ones available to install
        for pkg in packages:
            # ignore packages already installed (these are already marked to be updated)
            if not self.yum.rpmdb.installed(pkg.name):
                exactmatch, matched, unmatched = yum.packages.parsePackages(pl.available, [pkg.name])

                # install packages with best matching architectures
                archs = {}
                for match in exactmatch:
                    archs[match.arch] = match
                arch = self.yum.arch.get_best_arch_from_list(archs.keys())
                if arch:
                    pkg = archs[arch]
                    if pkg:
                        if snap.config.options.log_level_at_least('verbose'):
                            snap.callback.snapcallback.message("Restoring package " + pkg.name);
                        self.yum.install(pkg)

        # build / run the transaction
        self.yum.buildTransaction()
        self.yum.processTransaction()
