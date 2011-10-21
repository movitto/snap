#!/usr/bin/python
#
# Defines a snapshot target, or an abstract entity of
#  which a snapshot can be made of / restored
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

class SnapshotTarget:
    """Abstract entity on which to perform and restore a snapshot"""

    # actual target backends snap implements
    backends = ['repos', 'packages', 'files', 'services']

    def backup(self, basedir):
         '''Take a snapshot of the target

            @param - basedir - directory which to store snapshot data in'''
         raise NotImplementedError()

    def restore(self, basedir):
        '''Restore any package management files previously backed up
           
           @param - basedir - directory which to restore snapshot from'''
        raise NotImplementedError()
