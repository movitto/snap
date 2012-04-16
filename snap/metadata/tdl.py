# Metadata pertaining to a imagefactory/oz tdl, a system description format
#  which we can store snap metadata in for use in many cloud providers
#  (as deployed via the http://aeolusproject.org)
#
# (C) Copyright 2012 Mo Morsi (mo@morsi.org)
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
from snap.filemanager import FileManager
from snap.exceptions  import MissingDirError
from snap.metadata.repo      import ReposRecordFile
from snap.metadata.package   import PackagesRecordFile

class TDLFile:
    """The tdl, the end result of the backup operation.
       This can be processed with imagefactory/oz"""
       

    def __init__(self, tdlfile, snapdirectory):
        '''initialize the tdl

        @param tdlfile - the path to the tdlfile to write
        @param snapdirectory - the path to the directory to compress/extract
        @raises - MissingDirError - if the snapdirectory is invalid
        '''
        if not os.path.isdir(snapdirectory):
            raise MissingDirError(snapdirectory + " is an invalid snap working directory ")
        self.tdlfile = tdlfile
        self.snapdirectory = snapdirectory

    def write(self):
        '''create a tdl from the snapdirectory

        @raises - MissingFileError - if the tdl cannot be created
        '''
        # contents of the tdl
        contents  = "<template>\n"
        contents += "  <name>snap-</name>\n"
        contents += "  <description>snap generated tdl</description>\n"

        # temp store the working directory, before changing to the snapdirectory
        cwd = os.getcwd()
        os.chdir(self.snapdirectory)

        # TODO store generic operating system information
        contents += "  <os>\n"
        contents += "    <name></name>\n"
        contents += "    <version></version>\n"
        contents += "    <arch></arch>\n"

        # populate repo list in tdl
        record = ReposRecordFile(self.snapdirectory + "/repos.xml")
        repos = record.read()
        for repo in repos:
            contents += "    <install type='url'>\n"
            contents += "      <url>"+repo.url+"</url>\n"
            contents += "    </install>\n"

        contents += "  </os>\n"

        # populate package list in tdl
        contents += "  <packages>\n"

        record = PackagesRecordFile(self.snapdirectory + "/packages.xml")
        packages = record.read()
        for pkg in packages:
          # TODO decode package (need to use package subsystem type from snapshot metadata)
          contents += "    <package>" + pkg.name + "</package>\n"

        contents += "  </packages>\n"

        # TODO populate service list + config in tdl
        
        # TODO populate file list in tdl (how to make those files available for image creation?)

        contents += "</template>"

        # create the tdl
        tdl = open(self.tdlfile, "w")
        tdl.write(contents)
        tdl.close()

        if snap.config.options.log_level_at_least('normal'):
            snap.callback.snapcallback.message("TDL " + self.tdlfile + " created")

        # restore the working directory
        os.chdir(cwd)
