#!/usr/bin/python
#
# snap package system general adaptor
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
#
# (C) Copyright 2007 Mohammed Morsi (movitto@yahoo.com)

import os
import imp
import sys

import snap
from snap.exceptions import *
from snap.files import FileManager
from snap.packagesystem import PackageSystemBase
from snap.snapoptions import PACKAGE_SYSTEMS_DIR
sys.path.append(PACKAGE_SYSTEMS_DIR)

class SnapPackageSystemAdaptor(PackageSystemBase):
    """ handles loading the configured package system and running the target functionality.
        acts as an exception safe proxy to the configured package system 
        
        @raises SnapPackageSystemException if an error occurs at any point"""

    # handle to the package system
    psystem=None

    def __init__(self, psname):
            '''
            initialize the packagesystem with the give name.
            the corresponding module will be loaded out of the packagesystem directory
            and target class instantiated

            @param psname - name of the package system to load
            '''

            flagged=False
            for packagesystemfile in FileManager.get_all_files(PACKAGE_SYSTEMS_DIR):
                if packagesystemfile.name == psname + 'packagesystem.py':
                    # Dynamically load the module
                    module_name, ext = os.path.splitext(packagesystemfile.name)
                    module_location = imp.find_module(module_name)
                    module = imp.load_module(module_name, *module_location)
                    globals()[module_name] = module
                    # Dynamically instantiate the class
                    classobj = eval(module_name + '.' + psname.capitalize() + 'PackageSystem')
                    self.psystem = classobj()
                    if isinstance(self.psystem, PackageSystemBase): # must derive from the package system base
                        flagged=True
                    break
            if not flagged: # package management system was not found
               snap.callback.snapcallback.error(" Error instantiaing package system ")
               raise SnapPackageSystemError

    ################################ Error handling wrappers to packagesystem API

    def get_installed_packages(self):
        try:
            return self.psystem.get_installed_packages()
        except:
            snap.callback.snapcallback.error(" Error getting installed packages ")
            raise SnapPackageSystemError

    def install_packages(self, packages):
        try:
            self.psystem.install_packages(packages)
        except:
            snap.callback.snapcallback.error(" Error restoring packages ")
            raise SnapPackageSystemError

    def backup(self, construct_dir):
        try:
            self.psystem.backup(construct_dir)
        except:
            snap.callback.snapcallback.warn(" Error backing up package system ")

    def restore(self, construct_dir):
        try:
            self.psystem.restore(construct_dir)
        except:
            snap.callback.snapcallback.warn(" Error restoring package system ")

    def get_file_status(self, fullpath):
        try:
            return self.psystem.get_file_status(fullpath)
        except:
            snap.callback.snapcallback.warn(" Error getting file status for " + fullpath)
