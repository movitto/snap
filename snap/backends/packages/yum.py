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

import yum

class Yum(snap.Target):
    '''implements the snap! packages target backend using the yum package system'''

    def __init__(self):
        self.yum = yum.YumBase();
        #yum.YumBase.__init__(self.yum)

        self.fs_root='/'

    def backup(self, basedir, include=[], exclude=[]):
        '''backup the packages installed locally'''
        if snap.config.options.log_level_at_least('verbose'):
            snap.callback.snapcallback.message("Backing up packages using yum backend");

        # retrieve installed packages
        packages=[]
        packagenames = Set()
        for pkg in self.yum.rpmdb:
            if not pkg.name in packagenames:
                if snap.config.options.log_level_at_least('verbose'):
                    snap.callback.snapcallback.message("Backing up package " + pkg.name);
                packagenames.add(pkg.name)
                packages.append(Package(pkg.name, pkg.version))

        # write record file to basedir
        record = PackagesRecordFile(basedir + "packages.xml")
        record.write(packages)

    def restore(self, basedir):
        '''restore the packages from the snapfile'''
        if snap.config.options.log_level_at_least('verbose'):
            snap.callback.snapcallback.message("Restoring packages using yum backend");

        # first update the system
        for pkg in self.yum.rpmdb:
            self.yum.update(pkg)
        self.yum.buildTransaction()
        self.yum.processTransaction()

        # FIXME use native yum interface instead of dispatching to command
        #  pl = self.doPackageLists('all')
	      #packagenames = []
        #  for package in packages:
        #      packagenames.append(package.name)
        #  # for (po, matched_value) in self.searchGenerator(['name'], [package.name]):
	      #dlpkgs = []
        #  exactmatch, matched, unmatched = yum.packages.parsePackages(pl.available, packagenames)
        #  exactmatch = yum.misc.unique(exactmatch)
        #  for po in exactmatch:
        #      debug('Installing ' + str(po))
        #      if not PS_FAILSAFE:
        #          self.install(po)
		    #      dlpkgs.append(po)
        #  if not PS_FAILSAFE:
        #      self.buildTransaction()
    	  #    self.downloadPkgs(dlpkgs)

        #      testcb = RPMTransaction(self, test=True)
    	  #    self.initActionTs()
    	  #    self.populateTs(keepold=0)
    	  #    tserrors = self.ts.test(testcb)
    	  #    del testcb
    	  #    if len(tserrors > 0):
    	  #	    raise yum.Errors.YumBaseError
    	  #    self.runTransaction(None)
    	  #    del self.ts
    
    	  #    self.initActionTs()
    	  #    self.populateTs(keepold=0)
    	  #    self.ts.check()
    	  #    self.ts.order()
    	  #
    	  #    cb = RPMTransaction(self)
    	  #    self.runTransaction(cb)

        # read files from the record file
        record = PackagesRecordFile(basedir + "packages.xml")
        sfiles = record.read()

        # handle kernel modules first
        #   and ignore kernel as it was previously updated
        packagenames = []
        kmods = []
        for pkg in packages:
            if snap.config.options.log_level_at_least('verbose'):
                snap.callback.snapcallback.message("Restoring package " + pkg.name);
            if re.match(r'kmod*', pkg.name.rstrip()) != None:
                kmods.append(pkg.name)
            elif pkg.name.rstrip() != 'kernel':
                packagenames.append(pkg.name)

        # install the kernel modules
        command = 'yum --nogpgcheck -y --installroot ' + fs_root + ' install '
        for pkg in kmods:
            command += pkg + ' ' 
        print command
        os.system(command)

        # install the rest of the packages
        command = 'yum --nogpgcheck -y --installroot ' + fs_root + ' install '
        for pkg in packagenames:
	        command += pkg + ' '
        print command
        os.system(command)

