#!/usr/bin/python
# base interface for snap callback system
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
#

class Callback:
    """Base callback interface through which snap informs clients of progress"""
    
    def message(self, msg):
        '''
        a generic message

        @param - the string message
        '''
        pass

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

    def backup_target(self, target):
        '''
        starting to backup the specified target

        @param - the string target being backed up
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
        
    def restore_target(self, target):
        '''
        starting to backup packages

        @param - the string target being backed up
        '''
        pass

    def post_backup(self):
        '''
        ending the restore process
        '''
        pass

# assign this to your SnapCallbackBase-derived callback to hookup the callback system
snapcallback=SnapCallbackBase()
