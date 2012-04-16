# Snap! base class and interface
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
import imp
import tempfile

import config, callback
from snap.osregistry        import OS, OSUtils
from snap.exceptions        import InsufficientPermissionError
from snap.filemanager       import FileManager
from snap.snapshottarget    import SnapshotTarget
from snap.metadata.snapfile import SnapFile
from snap.outputformatter   import OutputFormatter

class SnapBase:
    def __init__(self):
        '''initialize snap '''

    def load_backends(self):
        '''
        Initialize the default backends for the targets with the give names.
        The default backends for the local os will be retrieved and the
        corresponding modules will be loaded out of the backends subdirectories
        and target classes instantiated and returned
        '''
        backends = {}

        for target in config.options.target_backends.keys():
            if config.options.target_backends[target]:
                backend = OS.default_backend_for_target(target)
                if backend != "disabled":
                    config.options.target_backends[target] = backend
    
                    # Dynamically load the module
                    backend_module_name = "snap.backends." + target + "." + backend
                    class_name = backend.capitalize()
                    backend_module = __import__(backend_module_name, globals(), locals(), [class_name])
    
                    # instantiate the backend class
                    backend_class = getattr(backend_module, class_name)
                    backend_instance = backend_class()
                    backends[target] = backend_instance

        return backends


    def check_permission(self):
        '''
        ensure current user has permissions to run Snap!

        @raises InsufficientPermissionError - if an error occurs when backing up the files
        '''
        if not OSUtils.is_superuser():
            raise InsufficientPermissionError("Must be root to run this program")

    def backup(self):
        '''
        peform the backup operation, recording installed packages and copying new/modified files
        '''
        if config.options.log_level_at_least('normal'):
            callback.snapcallback.message("Creating snapshot")

        self.check_permission()

        # temp directory used to construct tarball 
        construct_dir = tempfile.mkdtemp()
        FileManager.make_dir(construct_dir)

        backends = self.load_backends()
        configured_targets = backends.keys()
        for target in SnapshotTarget.BACKENDS: # load from SnapshotTarget to preserve order
          if target in configured_targets:
            backend = backends[target]
            includes = config.options.target_includes[target]
            excludes = config.options.target_excludes[target]
            backend.backup(construct_dir, include=includes, exclude=excludes)

        OutputFormatter.create(config.options.outputformat,
                 outfile=config.options.snapfile,
                 snapdirectory=construct_dir,
                 encryption_password=config.options.encryption_password)

        if config.options.log_level_at_least('normal'):
            callback.snapcallback.message("Snapshot completed")

        FileManager.rm_dir(construct_dir)

    def restore(self):
        '''
        perform the restore operation, restoring packages and files recorded
        '''
        if config.options.log_level_at_least('normal'):
            callback.snapcallback.message("Restoring Snapshot")

        self.check_permission()

        # temp directory used to extract tarball
        construct_dir = tempfile.mkdtemp()
        FileManager.make_dir(construct_dir)

        OutputFormatter.retrieve(config.options.outputformat,
                 infile=config.options.snapfile,
                 snapdirectory=construct_dir,
                 encryption_password=config.options.encryption_password)

        backends = self.load_backends()
        configured_targets = backends.keys()
        for target in SnapshotTarget.BACKENDS: # load from SnapShotTarget to preserve order
          if target in configured_targets:
            backend = backends[target]
            backend.restore(construct_dir)

        if config.options.log_level_at_least('normal'):
            callback.snapcallback.message("Restore completed")

        FileManager.rm_dir(construct_dir)
