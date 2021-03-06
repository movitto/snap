# Methods to backup/restore repositories using yum, implementing snap.SnapshotTarget
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
import re

import snap
from snap.metadata.sfile import SFile
from snap.metadata.repo  import Repo, ReposRecordFile
from snap.filemanager import FileManager

class Syum(snap.snapshottarget.SnapshotTarget):
    '''implements the snap! repos target backend using the yum package system'''

    def __init__(self):
        self.fs_root='/'

    def backup(self, basedir, include=[], exclude=[]):
        '''backup yum configuration and repositories'''
        # first backup the yum config
        SFile("/etc/yum.conf").copy_to(basedir)

        # then backup the individual repo files
        repos = []
        for yum_repo in FileManager.get_all_files(include=['/etc/yum.repos.d']):
            SFile(yum_repo).copy_to(basedir)

            # parse/extract repo info
            baseurl = re.compile('baseurl=(.*)\n')
            mirrorlist = re.compile('mirrorlist=(.*)\n')
            contents = FileManager.read_file(yum_repo)
            for match in baseurl.findall(contents):
                repos.append(Repo(url=match))
            for match in mirrorlist.findall(contents):
                repos.append(Repo(url=match))

        # write record file to basedir
        record = ReposRecordFile(basedir + "/repos.xml")
        record.write(repos)
          
    def restore(self, basedir):
        '''restore yum configuration and repositories'''
        # return if we cannot find require files
        if not os.path.isdir(basedir + "/etc/yum.repos.d"):
            return

        # read files from the record file
        # tho we don't do anything with this info here
        record = ReposRecordFile(basedir + "/repos.xml")
        repos = record.read()

        # first restore yum configuration
        SFile("etc/yum.conf").copy_to(self.fs_root, path_prefix=basedir)

        # then restore individual repos
        for yum_repo in FileManager.get_all_files(include=[basedir + "/etc/yum.repos.d"]):
            partial_path = yum_repo.replace(basedir + "/" , "")
            SFile(partial_path).copy_to(self.fs_root, path_prefix=basedir)

        # update the system
        # TODO Replace this w/ the right api call at some point
        #os.system("yum -y update")
