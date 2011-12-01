# Mock methods to backup/restore files, implementing snap.SnapshotTarget
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
from snap.snapshottarget import SnapshotTarget

class Mock(SnapshotTarget):
    '''mock implementation of the snap! files target backend'''

    backup_called  = False
    restore_called = False

    def backup(self, basedir, include=[], exclude=[]):
        """simply flag that backup has been called"""
        Mock.backup_called = True

    def restore(self, basedir):
        """simply flag that restore has been called"""
        Mock.restore_called = True
