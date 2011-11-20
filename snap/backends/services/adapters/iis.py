#!/usr/bin/python
#
# IIS service backup/restoration adapter for windows
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
import subprocess

import snap
from snap.osregistry import OS, OSUtils
from snap.metadata.sfile import SFile, FilesRecordFile
from snap.backends.services.dispatcher import Dispatcher
from snap.backends.services.windowsdispatcher import WindowsDispatcher

class Iis:

    CONFIG_ROOT = "C:\\Windows\\System32\\inetsrv\\config"
    WEBSERVER_FEATURE = "IIS-WebServer"
    #WEBSERVER_FEATURE_PATTERN = "IIS-.*" # TODO at some point backup/restore specific iis features as well

    def is_available(self):
        '''check service to see if it is enabled'''
        return WindowsDispatcher.is_feature_enabled(Iis.WEBSERVER_FEATURE)

    def install_prereqs(self):
        '''enable all IIS webserver features'''
        WindowsDispatcher.enable_feature(Iis.WEBSERVER_FEATURE)

    def backup(self, basedir):
        # backup the configuration directory
        sfiles = []
        files = snap.filemanager.FileManager.get_all_files(include_dirs=[Iis.CONFIG_ROOT])
        for tfile in files:
            if os.access(tfile, os.R_OK):
                sfile = SFile(tfile)
                sfile.copy_to(basedir)
                sfiles.append(sfile)

        # write record file to basedir
        record = FilesRecordFile(os.path.join(basedir, "service-iis.xml"))
        record.write(sfiles)

    def restore(self, basedir):
        out = open(OSUtils.null_file(), 'w')
        record_file = os.path.join(basedir, "service-iis.xml")
        
        # if files record file isn't found, simply return
        if not os.path.isfile(record_file):
            return

        # stop the httpd service if already running
        if WindowsDispatcher.is_feature_enabled(Iis.WEBSERVER_FEATURE):
            WindowsDispatcher.disable_feature(Iis.WEBSERVER_FEATURE)

        # read files from the record file
        record = FilesRecordFile(record_file)
        sfiles = record.read()

        # restore those to their original locations
        for sfile in sfiles:
            try:
                sfile.copy_to(path_prefix=basedir)
            except IOError, e:
                pass # just silently ignore errors for now

        # start the httpd service
        WindowsDispatcher.enable_feature(Iis.WEBSERVER_FEATURE)

        # restart iis
        popen = subprocess.Popen(['IISReset', '/restart'], stdout=out, stderr=out)
        popen.wait()
