#!/usr/bin/python
#
# Methods to dispatch service backup/restore operations to specific handlers
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

from snap.metadata.service import Service, ServicesRecordFile

# TODO at some point support a directory for snap services configuration,
#   something like /etc/snap.d/ where specific configurations for various
#   services to backup / restore can be stored


import snap
import subprocess

class Dispatcher(snap.snapshottarget.SnapshotTarget):
    '''implements the snap! services target backend, dispatching to handlers '''

    #def __init__(self):

    def service_running(service):
        '''helper to return boolean indicating if the specified service is running'''
        out=open('/dev/null', 'w')
        popen = subprocess.Popen(["service", service, "status"], stdout=out, stderr=out)
        popen.wait()
        return popen.returncode == 0
    service_running=staticmethod(service_running)

    def start_service(service):
        '''helper to start the specified service
        
        @returns boolean indicating if service was started or not'''
        out=open('/dev/null', 'w')
        popen = subprocess.Popen(["service", service, "start"], stdout=out, stderr=out)
        popen.wait()
        return popen.returncode == 0
    start_service=staticmethod(start_service)

    def stop_service(service):
        '''helper to stop the specified service
        
        @returns boolean indicating if service was stopped or not'''
        out=open('/dev/null', 'w')
        popen = subprocess.Popen(["service", service, "stop"], stdout=out, stderr=out)
        popen.wait()
        return popen.returncode == 0
    stop_service=staticmethod(stop_service)

    def load_service(self, service):
        '''initialize the specified service adapter'''

        # Dynamically load the module
        service_module_name = "snap.backends.services.adapters." + service
        class_name =  service.capitalize()
        service_module = __import__(service_module_name, globals(), locals(), [class_name])

        # instantiate the backend class
        service_class = getattr(service_module, class_name)
        service_instance = service_class()

        return service_instance

    def backup(self, basedir, include=[], exclude=[]):
        """run backup on each of the services included"""
        services = []

        for service in include:
            if snap.config.options.log_level_at_least('verbose'):
                snap.callback.snapcallback.message("Backing up service " + service);
            service_instance = self.load_service(service)
            sservice = service_instance.backup(basedir)
            services.append(Service(name=service))

        record = ServicesRecordFile(basedir + "/services.xml")
        record.write(services)

    def restore(self, basedir):
        """run restore on the snapfile"""

        record = ServicesRecordFile(basedir + "/services.xml")
        services = record.read()

        for sservice in services:
            if snap.config.options.log_level_at_least('verbose'):
                snap.callback.snapcallback.message("Restoring service " + sservice.name);
            service_instance = self.load_service(sservice.name)
            service_instance.restore(basedir)
        
