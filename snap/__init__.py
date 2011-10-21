#!/usr/bin/python
#
# Snap! base class and interface
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
import time

import snap
from snap.exceptions        import InsufficientPermissionError
from snap.filesmanager      import FileManager
from snap.metadata.snapfile import SnapFile
from snap.configmanager     import ConfigOptions

class SnapBase:
    # configuration options
    options = None

    # current time
    current_time = None

    # temp directory used to construct tarball 
    construct_dir = None

    def __init__(self):
        '''initialize snap '''

        self.options = ConfigOptions()
        self.current_time = time.strftime('%m.%d.%Y-%H.%M.%S') 
        self.construct_dir = '/tmp/snap-' + self.current_time

    def load_backends(self):
        '''
        Initialize the default backends for the targets with the give names.
        The default backends for the local os will be retrieved and the
        corresponding modules will be loaded out of the backends subdirectories
        and target classes instantiated and returned
        '''
        backends = []

        os = OS.lookup()
        for target in self.options.target_backends.keys():
            backend = OS.default_backend_for_target(os, target)
            self.options.target_backends[target] = backend

            # Dynamically load the module
            backend_file = os.path.dirname(__file__) + '/backends/' + target + '/' + backend + '.py'
            module_name, ext = os.path.splitext(backend_file)
            module_location = imp.find_module(module_name)
            module = imp.load_module(module_name, *module_location)
            globals()[module_name] = module

            # Dynamically instantiate the class
            classobj = eval(module_name + '.' + backend.capitalize())
            backends.append(classobj())

        return backends


    def check_permission(self):
        '''
        ensure current user has permissions to run Snap!

        @raises InsufficientPermissionError - if an error occurs when backing up the files
        '''
        if os.geteuid() != 0:
            snap.callback.snapcallback.error("Must be root to run this program")
            raise InsufficientPermissionError

    def backup(self, installed_packages = None):
        '''
        peform the backup operation, recording installed packages and copying new/modified files
        '''
        self.check_permission()
        snap.callback.snapcallback.init_backup()
        FileManager.make_dir(self.construct_dir)
        backends = self.load_backends()
        for backend in backends:
          backend.backup(self.construct_dir) # FIXME include/exclude targets support

        SnapFile(self.options.snapfile + '-' + self.current_time + '.tgz', self.construct_dir).compress()
        snap.callback.snapcallback.post_backup()

    def restore(self):
        '''
        perform the restore operation, restoring packages and files recorded
        '''
        self.check_permission()
        snap.callback.snapcallback.init_restore()
        FileManager.make_dir(self.construct_dir)
        backends = self.load_backends()
        SnapFile(self.options.snapfile, self.construct_dir).extract()

        for backend in backends:
          backend.restore(self.construct_dir)

        snap.callback.snapcallback.post_restore()
