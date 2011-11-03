#!/usr/bin/python
#
# HTTPD service backup/restoration adapter
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
import pwd
import tempfile
import subprocess

import snap
from snap.metadata.sfile import SFile, FilesRecordFile
from snap.backends.services.dispatcher import Dispatcher

class Httpd:

    if snap.osregistry.OS.yum_based():
        DAEMON='httpd'
        CONF_D='/etc/httpd'

        # hack until we re-introduce package system abstraction:
        PREREQ_INSTALL_COMMAND='yum install -y httpd'

    elif snap.osregistry.OS.apt_based():
        DAEMON='apache2'
        CONF_D='/etc/apache2'

        # hack until we re-introduce package system abstraction:
        PREREQ_INSTALL_COMMAND='apt-get install -y apache2'

    DOCUMENT_ROOT='/var/www'


    def is_available(self):
        '''return true if we're on a linux system and the init script is available'''
        return snap.osregistry.OS.is_linux() and os.path.isfile("/etc/init.d/" + Httpd.DAEMON)

    def install_prereqs(self):
        popen = subprocess.Popen(Httpd.PREREQ_INSTALL_COMMAND.split())
        popen.wait()

    def backup(self, basedir):
       # backup the webroot, confd
       sfiles = []
       files = snap.filemanager.FileManager.get_all_files(include_dirs=[Httpd.DOCUMENT_ROOT, Httpd.CONF_D])
       for tfile in files:
           if os.access(tfile, os.R_OK):
               sfile = SFile(tfile)
               sfile.copy_to(basedir)
               sfiles.append(sfile)

       # write record file to basedir
       record = FilesRecordFile(basedir + "/service-http.xml")
       record.write(sfiles)

    def restore(self, basedir):
        # if files record file isn't found, simply return
        if not os.path.isfile(basedir + "/service-http.xml"):
            return

        # read files from the record file
        record = FilesRecordFile(basedir + "/service-http.xml")
        sfiles = record.read()

        # restore those to their original locations
        for sfile in sfiles:
            sfile.copy_to('/', basedir)

        # stop the httpd service if already running
        if Dispatcher.service_running(Httpd.DAEMON):
            Dispatcher.stop_service(Httpd.DAEMON)

        # start the httpd service
        Dispatcher.start_service(Httpd.DAEMON)
