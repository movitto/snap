#!/usr/bin/python
#
# base package system class
#
# (C) Copyright 2007 Mohammed Morsi (movitto@yahoo.com)
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

class PackageSystemBase:
    """The base package system class from which all specific package
       system implementations should derive from.
       All methods require implementation"""

    def backup(self, basedir):
         '''Backup any configuration files, repository files, and anything
            else needed to restore the package management system into 
            it's exact current state

            @param - basedir - directory which to store files in'''
         raise NotImplementedError()

    def restore(self, basedir):
        '''Restore any package management files previously backed up
           
           @param - basedir - directory which to start restoration from'''

        raise NotImplementedError()

    def update_system(self):
        '''Perform any actions needed to update the current system before
            any new packages are installed '''
        raise NotImplementedError()

    def get_installed_packages(self):
        '''Return a list of packages.Package for each installed package
           in the system. Each package should contain all the 
           required data to be fully used by snap (including all 
           config options)
        '''
        raise NotImplementedError()

    def install_package(self,packages):
        '''Install the given list of packages.Package'
    
           @param - packages - the list of packages to install
        '''
        raise NotImplementedError()

    def get_file_status(self,file_name):
        ''''Returns True if the file in the given path is "marked", else
            False. A marked package is one that is not tracked by the
            Package Management System or one that has been modified 
            since it was installed'
            
            @param - file_name - path to the file which to check the status of
        '''
        # TODO the return status should be improved
        raise NotImplementedError()
