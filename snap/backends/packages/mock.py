#!/usr/bin/python
#
# Mock methods to backup/restore packages, implementing snap.SnapshotTarget.
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

class Mock(snap.Target):
    '''mock implementation of the snap! files target backend'''

    backup_called  = False
    restore_called = False

    def backup(self, basedir, include=[], exclude=[]):
        """simply flag that backup has been called"""
        backup_called = True

    def restore(self, basedir):
        """simply flag that restore has been called"""
        restore_called = True
