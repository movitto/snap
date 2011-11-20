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

import os

import snap
from snap.osregistry import OS
from snap.metadata.service import Service, ServicesRecordFile

class Dispatcher(snap.snapshottarget.SnapshotTarget):
    '''implements the snap! services target backend, dispatching to handlers '''
    
    def os_dispatcher():
        '''helper to get the os specific dispatcher'''
        if OS.is_windows():
            import snap.backends.services.windowsdispatcher
            return snap.backends.services.windowsdispatcher.WindowsDispatcher
        else:
            import snap.backends.services.linuxdispatcher
            return snap.backends.services.linuxdispatcher.LinuxDispatcher
    os_dispatcher = staticmethod(os_dispatcher)

    def load_service(self, service):
        '''initialize the specified service adapter'''

        # Dynamically load the module
        service_module_name = "snap.backends.services.adapters." + service
        class_name = service.capitalize()
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
            # check if service is running / available on machine b4 backing up
            if service_instance.is_available():
                sservice = service_instance.backup(basedir)
                services.append(Service(name=service))

        record = ServicesRecordFile(basedir + "/services.xml")
        record.write(services)

    def restore(self, basedir):
        """run restore on the snapfile"""
        # if files record file isn't found, simply return
        if not os.path.isfile(basedir + "/services.xml"):
            return

        record = ServicesRecordFile(basedir + "/services.xml")
        services = record.read()

        for sservice in services:
            if snap.config.options.log_level_at_least('verbose'):
                snap.callback.snapcallback.message("Restoring service " + sservice.name);
            service_instance = self.load_service(sservice.name)
            # install the prerequisites if the services is not available
            if not service_instance.is_available():
                service_instance.install_prereqs()
            
            if service_instance.is_available():
                service_instance.restore(basedir)
                
            # if service is still not available, log this and skip it    
            elif snap.config.options.log_level_at_least('normal'):
                snap.callback.snapcallback.message("Could not restore " + sservice.name + " service")
