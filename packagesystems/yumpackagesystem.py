#!/bin/python
#
# Snap wrapper to Yum Package Management System
#
# (C) Copyright 2007 Mohammed Morsi (movitto@yahoo.com)
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
import re
from sets import Set

from snap.packagesystem import PackageSystemBase
from snap.packages import Package
from snap.files import FileManager
from snap.snapoptions import *

import yum

class YumPackageSystem(PackageSystemBase, yum.YumBase):
    def __init__(self):
        yum.YumBase.__init__(self)

    def backup(self, basedir):
        if not os.path.exists(basedir + '/etc'):
            os.mkdir(basedir + '/etc')
        FileManager.copy_file(FileManager.get_file('/etc/yum.conf'), basedir + '/etc')
        if not os.path.exists(basedir + '/etc/yum.repos.d/'):
            os.mkdir(basedir + '/etc/yum.repos.d/')
        for fle in FileManager.get_all_files('/etc/yum.repos.d'):
            FileManager.copy_file(fle, basedir + '/etc/yum.repos.d')
#        if not os.path.exists(basedir + '/etc/pki/rpm-gpg/'):
#            if not os.path.exists(basedir + '/etc/pki/'):
#                os.mkdir(basedir + '/etc/pki/')
#            os.mkdir(basedir + '/etc/pki/rpm-gpg/')
#        for fle in FileManager.get_all_files('/etc/pki/rpm-gpg'):
#            FileManager.copy_file(fle, basedir + '/etc/pki/rpm-gpg')

    def restore(self, basedir):
        FileManager.copy_file(FileManager.get_file(basedir + '/etc/yum.conf'), '/etc')
        for fle in FileManager.get_all_files(basedir + '/etc/yum.repos.d'):
            FileManager.copy_file(fle, '/etc/yum.repos.d' )
#        for fle in FileManager.get_all_files(basedir + '/etc/pki/rpm-gpg'):
#            FileManager.copy_file(fle, '/etc/pki/rpm-gpg')
        # Replace this w/ the right api call at some point
        os.system("yum -y update")

    def update_system(self):
        for pkg in self.rpmdb:
            self.update(pkg)
        if not PS_FAILSAFE:
            self.buildTransaction()
            self.processTransaction()

    def get_installed_packages(self):
        packages=[]
        packagenames = Set()
        for pkg in self.rpmdb:
            if not pkg.name in packagenames:
                packagenames.add(pkg.name)
                packages.append(Package(pkg.name, pkg.version))
        return packages

    def install_packages(self, packages):
	# to save time, the yum command is just run
	# i started improving this (see yumpackagesystem.py.orig) 
	# but it doesn't work so feel free to fix and send a patch
        packagenames = []
        kmods = []
        for pkg in packages:
            if re.match(r'kmod*', pkg.name.rstrip()) != None: # handle kernel modules first
                kmods.append(pkg.name)
            elif pkg.name.rstrip() != 'kernel': # ignore kernel as it was previously updated
                packagenames.append(pkg.name)

        command = 'yum --nogpgcheck -y install '
        for pkg in kmods:
            command += pkg + ' ' 
        print command
        os.system(command)

        command = 'yum --nogpgcheck -y install '
        for pkg in packagenames:
	    command += pkg + ' '
        print command
        os.system(command)


    def get_file_status(self,file_name):
        status = True
        # Get all packages that provide the file
        pkgs = self.rpmdb.getProvides(file_name)
        # If there is a package that provides it, it is not new
        if len(pkgs) != 0:
            status = False
        for pkg in pkgs: # need just one failure (TODO?)
            # if file modification time > buildtime
            if os.stat(file_name).st_mtime > pkg.hdr["buildtime"]:
                status = True
        return status
