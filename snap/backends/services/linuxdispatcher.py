#!/usr/bin/python
#
# Methods to dispatch service backup/restore operations to specific handlers
#   on non-windows systems
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

from snap.metadata.service import Service, ServicesRecordFile

import snap
import subprocess
from snap.osregistry import OSUtils
from snap.backends.services.dispatcher import Dispatcher

class LinuxDispatcher(Dispatcher):
    '''implements the snap! services target backend, dispatching to handlers '''

    def service_running(service):
        '''helper to return boolean indicating if the specified service is running'''
        out = open(OSUtils.null_file(), 'w')
        popen = subprocess.Popen(["service", service, "status"], stdout=out, stderr=out)
        popen.wait()
        return popen.returncode == 0
    service_running = staticmethod(service_running)

    def start_service(service):
        '''helper to start the specified service
        
        @returns boolean indicating if service was started or not'''
        out = open(OSUtils.null_file(), 'w')
        popen = subprocess.Popen(["service", service, "start"], stdout=out, stderr=out)
        popen.wait()
        return popen.returncode == 0
    start_service = staticmethod(start_service)

    def stop_service(service):
        '''helper to stop the specified service
        
        @returns boolean indicating if service was stopped or not'''
        out = open(OSUtils.null_file(), 'w')
        popen = subprocess.Popen(["service", service, "stop"], stdout=out, stderr=out)
        popen.wait()
        return popen.returncode == 0
    stop_service = staticmethod(stop_service)
