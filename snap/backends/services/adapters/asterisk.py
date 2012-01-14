# Asterisk telephony server backup and restore
#
# (C) Copyright 2012 Russell Bryant (russell@russellbryant.net)
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


class Asterisk:

    DAEMON = 'asterisk'

    DIRS = {
        # All of the configuration files
        'conf': '/etc/asterisk',
        # Call recordings, voicemails, ...
        'spool': '/var/spool/asterisk',
        # Music on Hold files, encryption keys, AGI scripts, ...
        'data': '/usr/share/asterisk',
    }

    PREREQ_INSTALL_COMMAND = None

    if OS.yum_based():
        # hack until we re-introduce package system abstraction:
        PREREQ_INSTALL_COMMAND = 'yum install -y asterisk'

    elif OS.apt_based():
        # hack until we re-introduce package system abstraction:
        PREREQ_INSTALL_COMMAND = 'apt-get install -y asterisk'

    @classmethod
    def is_available(cls):
        '''return true if we're on a linux and the config dir exists'''
        return OS.is_linux() and os.path.isdir(Asterisk.DIRS['conf'])

    @classmethod
    def install_prereqs(cls):
        if OS.is_linux():
            subprocess.Popen(Asterisk.PREREQ_INSTALL_COMMAND.split()).wait()

    @classmethod
    def backup(cls, basedir):
        # backup the confd
        files = snap.filemanager.FileManager.get_all_files(
                             include=[d for d in Asterisk.DIRS.itervalues()])
        sfiles = [SFile(tfile).copy_to(basedir)
                             for tfile in files if os.access(tfile, os.R_OK)]

        # write record file to basedir
        record = FilesRecordFile(os.path.join(basedir, "service-asterisk.xml"))
        record.write(sfiles)

    @classmethod
    def restore(cls, basedir):
        dispatcher = Dispatcher.os_dispatcher()

        record_file = os.path.join(basedir, "service-asterisk.xml")

        # if files record file isn't found, simply return
        if not os.path.isfile(record_file):
            return

        # stop the service if already running
        if dispatcher.service_running(Asterisk.DAEMON):
            dispatcher.stop_service(Asterisk.DAEMON)

        # read files from the record file
        record = FilesRecordFile(record_file)
        sfiles = record.read()

        # restore those to their original locations
        for sfile in sfiles:
            sfile.copy_to(path_prefix=basedir)

        # start the service
        dispatcher.start_service(Asterisk.DAEMON)
