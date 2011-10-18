#!/usr/bin/python
#
# snap base class and interface
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

import os    # to save/restore the initial cwd
import time  # to generate snapfile name incorporating current time

import snap
from snap.exceptions import *
from snap.files import FileManager,SnapFile
from snap.packages import PackageFile
from snap.configmanager import ConfigOptions
from snap.packagesystemadaptor import SnapPackageSystemAdaptor

class SnapBase:
    # configuration options
    options = None

    # current time
    current_time = None

    # temp directory used to construct tarball 
    construct_dir = None

    # saved cwd
    cwd = None

    def __init__(self):
        '''initialize snap '''

        self.options = ConfigOptions()
        self.current_time = time.strftime('%m.%d.%Y-%H.%M.%S') 
        self.construct_dir = '/tmp/snap-' + self.current_time
        self.cwd = os.getcwd()

    def check_permission(self):
        if os.geteuid() != 0:
            snap.callback.snapcallback.error("Must be root to run this program")
            raise SnapInsufficientPermissionError

    def backup(self, installed_packages = None):
        '''
        peform the backup operation, recording installed packages and copying new/modified files

        @param installed_packages - optional list of snap.packages.Package to install
        @raises SnapPackageSystemError - if an error occurs when backing up the packages
        @raises SnapFileSystemError - if an error occurs when backing up the files
        '''
        self.check_permission()
        snap.callback.snapcallback.init_backup()
        FileManager.make_dir(self.construct_dir)
        psa = SnapPackageSystemAdaptor(self.options.packagesystem)

        if self.options.handlepackages:
            if installed_packages == None:
                installed_packages = psa.get_installed_packages()
            PackageFile(self.construct_dir + '/packages.xml').write(installed_packages)
            psa.backup(self.construct_dir) 

        if self.options.handlefiles:
            dir = '/'
            if self.options.include != None and self.options.include != '':
                dir = self.options.include
            files = FileManager.get_all_files(dir, self.options.exclude, psa)
            FileManager(self.construct_dir + '/files.xml', self.construct_dir).backup(files)

        SnapFile(self.options.snapfile + '-' + self.current_time + '.tgz', self.construct_dir).compress()
        snap.callback.snapcallback.post_backup()
        os.chdir(self.cwd)

    def restore(self):
        '''
        perform the restore operation, restoring packages and files recorded

        @raises SnapPackageSystemError - if an error occurs when restoring the packages
        @raises SnapFileSystemError - if an error occurs when restoring the files
        '''
        self.check_permission()
        snap.callback.snapcallback.init_restore()
        FileManager.make_dir(self.construct_dir)
        psa = SnapPackageSystemAdaptor(self.options.packagesystem)
        SnapFile(self.options.snapfile, self.construct_dir).extract()

        if self.options.handlepackages:
        	psa.restore(self.construct_dir) 
        	installed_packages = PackageFile(self.construct_dir + '/packages.xml').read()
        	psa.install_packages(installed_packages)

        if self.options.handlefiles:
            FileManager(self.construct_dir + '/files.xml', self.construct_dir).restore()

        snap.callback.snapcallback.post_restore()
        os.chdir(self.cwd)
