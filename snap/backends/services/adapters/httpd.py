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
import subprocess

import snap
from snap.osregistry import OS, OSUtils
from snap.metadata.sfile import SFile, FilesRecordFile
from snap.backends.services.dispatcher import Dispatcher

class Httpd:

    if OS.yum_based():
        DAEMON = 'httpd'
        CONF_D = '/etc/httpd'
        DOCUMENT_ROOT = '/var/www'

        # hack until we re-introduce package system abstraction:
        PREREQ_INSTALL_COMMAND = 'yum install -y httpd'

    elif OS.apt_based():
        DAEMON = 'apache2'
        CONF_D = '/etc/apache2'
        DOCUMENT_ROOT = '/var/www'

        # hack until we re-introduce package system abstraction:
        PREREQ_INSTALL_COMMAND = 'apt-get install -y apache2'
        
    elif OS.is_windows() and os.path.isdir("C:\Program Files (x86)\Apache Software Foundation"):
        DAEMON = 'Apache2.2'
        CONF_D = "C:\\Program Files (x86)\\Apache Software Foundation\\Apache2.2\\conf"
        DOCUMENT_ROOT = "C:\\Program Files (x86)\\Apache Software Foundation\\Apache2.2\\htdocs"
    
    else:
        DAEMON = None
        CONF_D = None
        DOCUMENT_ROOT = None

    def is_available(self):
        '''return true if we're on a linux system and the init script is available'''
        return (Httpd.CONF_D and os.path.isdir(Httpd.CONF_D) and 
                Httpd.DOCUMENT_ROOT and os.path.isdir(Httpd.DOCUMENT_ROOT))

    def install_prereqs(self):
        if OS.is_linux():
            popen = subprocess.Popen(Httpd.PREREQ_INSTALL_COMMAND.split())
            popen.wait()
        # !!!FIXME!!! it is possible to install httpd in an automated / 
        # non-interactive method on windows, implement this!!!

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
       record = FilesRecordFile(os.path.join(basedir, "service-http.xml"))
       record.write(sfiles)

    def restore(self, basedir):
        dispatcher = Dispatcher.os_dispatcher()
        
        record_file = os.path.join(basedir, "service-http.xml")
        
        # if files record file isn't found, simply return
        if not os.path.isfile(record_file):
            return

        # stop the httpd service if already running
        if dispatcher.service_running(Httpd.DAEMON):
            dispatcher.stop_service(Httpd.DAEMON)
            
        # read files from the record file
        record = FilesRecordFile(record_file)
        sfiles = record.read()

        # restore those to their original locations
        for sfile in sfiles:
            sfile.copy_to(path_prefix=basedir)

        # ensure the various subdirs exists even if empty
        if OS.is_linux() and not os.path.isdir(os.path.join(Httpd.DOCUMENT_ROOT, "html")):
            os.mkdir(os.path.join(Httpd.DOCUMENT_ROOT, "html"))
        if OS.is_linux() and not os.path.isdir(os.path.join(Httpd.CONF_D, "logs")):
            os.mkdir(os.path.join(Httpd.CONF_D, "logs"))
        if OS.is_linux() and not os.path.isdir(os.path.join(Httpd.CONF_D, "run")):
            os.mkdir(os.path.join(Httpd.CONF_D, "run"))


        # start the httpd service
        dispatcher.start_service(Httpd.DAEMON)
