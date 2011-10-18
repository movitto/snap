#!/bin/python
#
# Snap wrapper to Yum Package Management System
# In Development. I began writing this snap plugin
#  to utilize the yum python api, but ended up going to
#  simply running system commands to save time. Feel
#  free to finish and send a patch
#
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

from snap.packagesystem import PackageSystemBase
from snap.packages import Package
from snap.files import FileManager
from snap.snapoptions import *

import yum
from yum.rpmtrans import RPMTransaction

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

    def restore(self, basedir):
	# TODO yum update yum
        FileManager.copy_file(FileManager.get_file(basedir + '/etc/yum.conf'), '/etc')
        for fle in FileManager.get_all_files(basedir + '/etc/yum.repos.d'):
            FileManager.copy_file(fle, './etc/yum.repos.d' )

    def update_system(self):
        for pkg in self.rpmdb:
            self.update(pkg)
        if not PS_FAILSAFE:
            self.buildTransaction()
            self.processTransaction()

    def get_installed_packages(self):
        packages=[]
        for pkg in self.rpmdb:
            packages.append(Package(pkg.name, pkg.version))
        return packages

    def install_packages(self, packages):
        pl = self.doPackageLists('all')
	    packagenames = []
        for package in packages:
            packagenames.append(package.name)
        # for (po, matched_value) in self.searchGenerator(['name'], [package.name]):
	    dlpkgs = []
        exactmatch, matched, unmatched = yum.packages.parsePackages(pl.available, packagenames)
        exactmatch = yum.misc.unique(exactmatch)
        for po in exactmatch:
            debug('Installing ' + str(po))
            if not PS_FAILSAFE:
                self.install(po)
		        dlpkgs.append(po)
        if not PS_FAILSAFE:
            self.buildTransaction()
    	    self.downloadPkgs(dlpkgs)

            testcb = RPMTransaction(self, test=True)
    	    self.initActionTs()
    	    self.populateTs(keepold=0)
    	    tserrors = self.ts.test(testcb)
    	    del testcb
    	    if len(tserrors > 0):
    		    raise yum.Errors.YumBaseError
    	    self.runTransaction(None)
    	    del self.ts
    
    	    self.initActionTs()
    	    self.populateTs(keepold=0)
    	    self.ts.check()
    	    self.ts.order()
    	
    	    cb = RPMTransaction(self)
    	    self.runTransaction(cb)

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
