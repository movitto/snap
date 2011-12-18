# Methods to backup/restore repositories using apt, implementing snap.SnapshotTarget
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

import snap
from snap.metadata.sfile import SFile
from snap.filemanager import FileManager

class Sapt(snap.snapshottarget.SnapshotTarget):
    '''implements the snap! repos target backend using the apt package system'''

    def __init__(self):
        self.fs_root='/'

    def backup(self, basedir, include=[], exclude=[]):
        '''backup apt configuration and repositories'''
        # backup the apt config in /etc/apt
        for apt_conf in FileManager.get_all_files(include=['/etc/apt']):
            SFile(apt_conf).copy_to(basedir)
          
    def restore(self, basedir):
        '''restore yum configuration and repositories'''
        # return if we cannot find require files
        if not os.path.isdir(basedir + "/etc/apt"):
            return

        # restore the apt config to /etc/apt
        for apt_conf in FileManager.get_all_files(include=[basedir + "/etc/apt"]):
            partial_path = apt_conf.replace(basedir + "/", "")
            SFile(partial_path).copy_to(self.fs_root, path_prefix=basedir)
