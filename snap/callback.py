#!/usr/bin/python
# base interface for snap callback system
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
#

class SnapCallbackBase:
    """This is the base class for the snap callback system through
       which snap updates a client as to the progress of its operations
       This class should be inherited and the following methods overridden 
       by clients who will handle the callback messages in their own means"""
    
    verbose=False

    def warn(self, warning):
        '''
        a non-critical warning

        @param - the string warning
        '''
        pass

    def error(self, error):
        '''
        critical error, program will terminate

        @param - the string error
        '''
        pass

    def init_backup(self):
        '''
        starting the backup process
        '''
        pass

    def backup_packages(self):
        '''
        starting to backup packages
        '''
        pass

    def backup_package(self, package):
        '''
        backed up a package

        @param - the snap.packages.Package that was backed up
        '''
        pass
        
    def backup_files(self):
        '''
        starting to backup files
        '''
        pass

    def backup_file(self, file):
        '''
        backed up a file

        @param - the snap.files.SFile that was backed up
        '''
        pass

    def snapfile_created(self, snapfile):
        '''
        created snapfile tarball

        @param - the snap.files.SnapFile created
        '''
        pass

    def post_backup(self):
        '''
        ending the backup process
        '''
        pass

    def init_restore(self):
        '''
        starting the restore process
        '''
        pass
        
    def restore_packages(self):
        '''
        starting to backup packages
        '''
        pass

    def restore_package(self, package):
        '''
        restored a package
        
        @param - the snap.packages.Package that was restored
        '''
        pass

    def restore_files(self):
        '''
        starting to restore files
        '''
        pass

    def restore_file(self, file):
        '''
        restored a file

        @param - the snap.files.SFile that was restored
        '''
        pass
        
    def snapfile_restored(self, snapfile):
        '''
        restored snapfile tarball

        @param - the snap.files.SnapFile restored
        '''
        pass

    def post_backup(self):
        '''
        ending the restore process
        '''
        pass


# assign this to your SnapCallbackBase-derivce callback to hookup the callback system
snapcallback=SnapCallbackBase()
