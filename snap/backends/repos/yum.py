#!/usr/bin/python
#
# Methods to backup/restore repositories using yum, implementing snap.SnapshotTarget
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

from snap.files import FileManager

class Yum(snap.Target):
    #def __init__(self):

    def backup(self, basedir, include=[], exclude=[]):
        '''backup yum configuration and repositories'''
        # first backup the yum config
        SFile("/etc/yum.conf").copy_to(basedir)

        # then backup the individual repo files
        for yum_repo in FileManager.get_all_files('/etc/yum.repos.d'):
            SFile(yum_repo).copy_to(basedir)
          
    def restore(self, basedir):
        '''restore yum configuration and repositories'''
        # first restore yum configuration
        SFile("/etc/yum.conf").copy_to("/", basedir)

        # then restore individual repos
        for yum_repo in FileManager.get_all_files(basedir + "/etc/yum.repos.d"):
            SFile(yum_repo).copy_to("/")

        # update the system
        # TODO Replace this w/ the right api call at some point
        #os.system("yum -y update")
