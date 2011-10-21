#!/usr/bin/python
#
# Snap! Configuration Manager
#
# (C) Copyright 2011 Mo Morsi (mo@morsi.org)
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

import os, os.path
import optparse, ConfigParser

import snap
from snapoptions import *

class ConfigOptions:
    """Container holding all the configuration options available
       to the Snap system"""

    # mode of operation
    mode=None

    # modes of operation
    RESTORE = 0
    BACKUP  = 1

    # mapping of targets to lists of backends to use when backing up / restoring them
    target_backends={}

    # mapping of targets to lists of entities to include when backing up
    target_includes={}

    # mapping of targets to lists of entities to exclude when backing up
    target_excludes={}

    # output log level
    # currently supports 'quiet', 'normal', 'verbose', 'debug'
    log_level='normal'

    # location of the snapfile to backup to / restore from
    snapfile=DEFAULT_SNAPFILE

    def __init__(self):
        '''initialize configuration'''
        for backend in SnapshotTarget.backends:
            target_backends[backend] = False
            target_includes[backend] = []
            target_excludes[backend] = []

    def log_level_at_least(comparison):
        return (comparison == 'quiet') or
               (comparison == 'normal'  and self.log_level != 'quiet') or
               (comparison == 'verbose' and (self.log_level == 'verbose' or self.log_level == 'debug')) or
               (comparison == 'debug'   and self.log_level  == 'debug')

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
                snap.callback.snapcallback.warn("Config file " + config_file +" not found")
        else:
            self.parser = ConfigParser.ConfigParser()
            self.parser.read(config_file)
            cfg.parse()

    def __string_to_bool(string):
        '''Static helper to convert a string to a boolean value'''
        if string == 'True' or string == 'true' or string == '1':
            return True
        elif string == 'False' or string == 'false' or string == '0':
            return False
        return None
    string_to_bool=staticmethod(string_to_bool)

    def __string_to_array(string):
        '''Static helper to convert a colon deliminated string to an array of strings'''
        return string.split(':')
    string_to_bool=staticmethod(string_to_array)

    def __get_bool(self, key, section = 'main'):
        '''
        Retreive the indicated boolean value from the config file

        @param key - the string key corresponding to the boolean value to retrieve
        @param section - the section to retrieve the value from
        @returns - the value or False if not found
        '''

        try:
            return Config.string_to_bool(self.parser.get(section, key))
        except:
            return None

    def __get_string(self, key, section = 'main'):
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

    def __parse(self):
        '''parse configuration out of the config file'''
        for backend in SnapshotTarget.backends:
            if val = get_bool(backend):
                self.configoptions.target_backends[backend] = val

            elif val = get_string(i) 
                self.configoptions.target_backends[backend] = True
                val = Config.string_to_array(val)
                for include in val:
                    if include[0] == '!':
                        self.configoptions.target_excludes[backend].append(include[1:])
                    else:
                        self.configoptions.target_includes[backend].append(include)
                      

            elif cfg.get_bool('no' + backend):
                self.configoptions.target_backends[i] = False

        sf = cfg.get_string('snapfile')
        ll = cfg.get_string('log-level')
        
        if sf != None:
            self.configoptions.snapfile = sf
        if ll != None:
            self.configoptions.log_level = ll

class Config:
    """The configuration manager, used to set and verify snap config values 
       from the config file and command line. Primary interface to the 
       Configuration System"""
    
    configoptions=None
    parser=None

    # read values from the config files and set them in the target ConfigOptions
    def read_config(self):
        debug('Parsing config')
        for config_file in CONFIG_FILES:
          cfg = Config(config_file)

    # Setup the parser to expect the values when parsing the command line
    def _setup_options(self):
        debug("Setting up options")
        usage = "usage: %prog [options] arg"
        self.parser = optparser.OptionParser(usage, version=SNAP_VERSION)
        self.parser.add_option('', '--restore', dest = 'restore', action='store_true', default=False, help='Restore snapshot')
        self.parser.add_option('', '--backup', dest = 'backup', action='store_true', default=False, help='Take snapshot')
        self.parser.add_option('-l', '--log-level', dest = 'log_level', action='store', default="normal", help='Log level (quiet, normal, verbose, debug)')
        self.parser.add_option('-f', '--snapfile', dest = 'snapfile', action='store', default=None, help='Snapshot file')
        for backend in SnapshotTarget.backends:
            self.parser.add_option('', '--'   + backend, dest = backend, action='store', default=None, help='Enable '  + backend + ' snapshots/restoration')
            self.parser.add_option('', '--no' + backend, dest = backend, action='store_false', default=False, help='Disable ' + backend + ' snapshots/restoration')

    def parse_cli(self):
        '''
        parses the command line an set them in the target ConfigOptions
        '''

        debug("Parsing command line")
        (options, args) = self.parser.parse_args()
        if options.restore != False:
            self.configoptions.mode = ConfigOptions.RESTORE
        if options.backup != False:
            self.configoptions.mode = ConfigOptions.BACKUP
        if options.log_level:
            self.configoptions.log_level=options.log_level
        if options.snapfile != None:
            self.configoptions.snapfile=options.snapfile
        for backend in SnapshotTarget.backends:
            val = getattr(options, backend)
            if val != None:
                if type(val) == str:
                    self.configoptions.target_backend[backend] = True
                    val = Config.string_to_array(val)
                    for include in val:
                        if include[0] == '!':
                            self.configoptions.target_excludes[backend].append(include[1:])
                        else:
                            self.configoptions.target_includes[backend].append(include)
                else:
                    self.configoptions.target_backend[backend] = val

    def verify_integrity(self):
        '''
        verify the integrity of the current option set

        @raises - SnapArgError if the options are invalid
        '''

        debug('Verifying Options Intgerity')
        if self.configoptions.mode == None: # mode not specified
            raise snap.exceptions.SnapArgError("Must specify backup or restore")
        if self.configoptions.mode == ConfigOptions.RESTORE and self.configoptions.snapfile == DEFAULT_SNAPFILE: # need to specify snapfile when restoring
            raise snap.exceptions.SnapArgError("Must specify snapfile")
        # Add any additional checks here

    def __init__(self, targetconfig):
        '''
        create the config manager 

        @param targetconfig - instance of ConfigOptions which to set values retrieved
                              from the config file and command line on
        '''

        self.configoptions=targetconfig
        self._setup_options()

# static shared options
options=ConfigOptions()
