# Snap! Configuration Manager
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
import os.path
import optparse, ConfigParser

import snap
from snap.options import *
from snap.snapshottarget import SnapshotTarget
from snap.exceptions import ArgError

class ConfigOptions:
    """Container holding all the configuration options available
       to the Snap system"""

    # modes of operation
    RESTORE = 0
    BACKUP = 1

    def __init__(self):
        '''initialize configuration'''

        # mode of operation
        self.mode = None

        # mapping of targets to lists of backends to use when backing up / restoring them
        self.target_backends = {}

        # mapping of targets to lists of entities to include when backing up
        self.target_includes = {}

        # mapping of targets to lists of entities to exclude when backing up
        self.target_excludes = {}

        # output log level
        # currently supports 'quiet', 'normal', 'verbose', 'debug'
        self.log_level = 'normal'

        # output format to backup / restore
        self.outputformat = 'snapfile'

        # location of the snapfile to backup to / restore from
        self.snapfile = None

        # Encryption/decryption password to use, if left as None, encryption will be disabled
        self.encryption_password = None
        
        # hash of key/value pairs of service-specific options
        self.service_options = {}

        for backend in SnapshotTarget.BACKENDS:
            self.target_backends[backend] = False
            self.target_includes[backend] = []
            self.target_excludes[backend] = []

    def log_level_at_least(self, comparison):
        return (comparison == 'quiet') or \
               (comparison == 'normal'  and self.log_level != 'quiet') or \
               (comparison == 'verbose' and (self.log_level == 'verbose' or self.log_level == 'debug')) or \
               (comparison == 'debug'   and self.log_level == 'debug')

class ConfigFile:
    """Represents the snap config file to be read and parsed"""

    parser = None

    def __init__(self, config_file):
        '''
        Initialize the config file, specifying its path

        @param file - the path to the file to load
        '''

        # if config file doesn't exist, just ignore
        if not os.path.exists(config_file):
            if snap.config.options.log_level_at_least("verbose"):
                snap.callback.snapcallback.warn("Config file " + config_file + " not found")
        else:
            self.parser = ConfigParser.ConfigParser()
            self.parser.read(config_file)
            self.__parse()

    def string_to_bool(string):
        '''Static helper to convert a string to a boolean value'''
        if string == 'True' or string == 'true' or string == '1':
            return True
        elif string == 'False' or string == 'false' or string == '0':
            return False
        return None
    string_to_bool = staticmethod(string_to_bool)

    def string_to_array(string):
        '''Static helper to convert a colon deliminated string to an array of strings'''
        return string.split(':')
    string_to_array = staticmethod(string_to_array)

    def __get_bool(self, key, section='main'):
        '''
        Retreive the indicated boolean value from the config file

        @param key - the string key corresponding to the boolean value to retrieve
        @param section - the section to retrieve the value from
        @returns - the value or False if not found
        '''

        try:
            return ConfigFile.string_to_bool(self.parser.get(section, key))
        except:
            return None

    def __get_string(self, key, section='main'):
        '''
        Retreive the indicated string value from the config file

        @param key - the string key corresponding to the string value to retrieve
        @param section - the section to retrieve the value from
        @returns - the value or None if not found
        '''

        try:
            return self.parser.get(section, key)
        except:
            return None
        
    def __get_array(self, section='main'):
        '''return array of key/value pairs from the config file section
        
        @param section - the section which to retrieve the key / values from
        @returns - the array of key / value pairs or None if not found
        '''
        try:
            return self.parser.items(section)
        except:
            return None
        
    def __parse(self):
        '''parse configuration out of the config file'''
        for backend in SnapshotTarget.BACKENDS:
            val = self.__get_bool(backend)
            if val is not None:
                snap.config.options.target_backends[backend] = val

            else:
                val = self.__get_string(backend) 
                if val:
                    snap.config.options.target_backends[backend] = True
                    val = ConfigFile.string_to_array(val)
                    for include in val:
                        if include[0] == '!':
                            snap.config.options.target_excludes[backend].append(include[1:])
                        else:
                            snap.config.options.target_includes[backend].append(include)

                else:
                    val = self.__get_bool('no' + backend)
                    if val:
                        snap.config.options.target_backends[backend] = False

        of = self.__get_string('outputformat')
        sf = self.__get_string('snapfile')
        ll = self.__get_string('loglevel')
        enp = self.__get_string('encryption_password')
        
        if of != None:
            snap.config.options.outputformat = of
        if sf != None:
            snap.config.options.snapfile = sf
        if ll != None:
            snap.config.options.log_level = ll
        if enp != None:
            snap.config.options.encryption_password = enp
            
        services = self.__get_array('services')
        if services:
            for k, v in services:
                snap.config.options.service_options[k] = v

class Config:
    """The configuration manager, used to set and verify snap config values 
       from the config file and command line. Primary interface to the 
       Configuration System"""
    
    configoptions = None
    parser = None

    # read values from the config files and set them in the target ConfigOptions
    def read_config(self):
        # add conf stored in resources if running from local checkout 
        CONFIG_FILES.append(os.path.join(os.path.dirname(__file__), "..", "resources", "snap.conf"))
        for config_file in CONFIG_FILES:
          ConfigFile(config_file)

    def parse_cli(self):
        '''
        parses the command line an set them in the target ConfigOptions
        '''

        usage = "usage: %prog [options] arg"
        self.parser = optparse.OptionParser(usage, version=SNAP_VERSION)
        self.parser.add_option('', '--restore', dest='restore', action='store_true', default=False, help='Restore snapshot')
        self.parser.add_option('', '--backup', dest='backup', action='store_true', default=False, help='Take snapshot')
        self.parser.add_option('-l', '--log-level', dest='log_level', action='store', default="normal", help='Log level (quiet, normal, verbose, debug)')
        self.parser.add_option('-o', '--outputformat', dest='outputformat', action='store', default=None, help='Output file format')
        self.parser.add_option('-f', '--snapfile', dest='snapfile', action='store', default=None, help='Snapshot file, use - for stdout')
        self.parser.add_option('-p', '--password', dest='encryption_password', action='store', default=None, help='Snapshot File Encryption/Decryption Password')
        # FIXME how to permit parameter lists for some of these
        for backend in SnapshotTarget.BACKENDS:
            self.parser.add_option('', '--' + backend, dest=backend, action='store_true', help='Enable ' + backend + ' snapshots/restoration')
            self.parser.add_option('', '--no' + backend, dest=backend, action='store_false', help='Disable ' + backend + ' snapshots/restoration')

        (options, args) = self.parser.parse_args()
        if options.restore != False:
            snap.config.options.mode = ConfigOptions.RESTORE
        if options.backup != False:
            snap.config.options.mode = ConfigOptions.BACKUP
        if options.log_level:
            snap.config.options.log_level = options.log_level
        if options.outputformat != None:
            snap.config.options.outputformat = options.outputformat
        if options.snapfile != None:
            snap.config.options.snapfile = options.snapfile
        if options.encryption_password != None:
            snap.config.options.encryption_password = options.encryption_password
        for backend in SnapshotTarget.BACKENDS:
            val = getattr(options, backend)
            if val != None:
                if type(val) == str:
                    snap.config.options.target_backends[backend] = True
                    val = ConfigFile.string_to_array(val)
                    for include in val:
                        if include[0] == '!':
                            snap.config.options.target_excludes[backend].append(include[1:])
                        else:
                            snap.config.options.target_includes[backend].append(include)
                else:
                    snap.config.options.target_backends[backend] = val

    def verify_integrity(self):
        '''
        verify the integrity of the current option set

        @raises - ArgError if the options are invalid
        '''
        if snap.config.options.mode == None: # mode not specified
            raise snap.exceptions.ArgError("Must specify backup or restore")
        if snap.config.options.snapfile == None: # need to specify snapfile location
            raise snap.exceptions.ArgError("Must specify snapfile")
        # TODO verify output format is one of permitted types
        if snap.config.options.outputformat == None: # need to specify output format
            raise snap.exceptions.ArgError("Must specify valid output format")

# static shared options
options = ConfigOptions()
