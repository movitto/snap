#!/usr/bin/python
#
# Snap Configuration Manager
#
# Options specified via config file:
#  packagesystem=[yum|apt-get|portage|swaret|...] - underlying package management system
#  default values for any of the command line options
#  
# Options specified via the command line:
#  --help      - standard help
#  --version   - standard version
#
#  --backup    - set mode to take snapshot
#  --restore   - set mode to restore snapshot
#  --v(erbose) - verbose output
#  --snapfile  - file which to generate / restore 
#              - time of snapshot and extension will be autoappended
#  --snaphost  - uri to host to store / retrieve snapshot (NOT IMPLEMENTED YET!!!)
#  --(no)files - disable/enable file backup / restoration
#  --include   - directories to backup
#  --exclude   - directions to exclude when backing up
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
#
# (C) Copyright 2007 Mohammed Morsi (movitto@yahoo.com)

import os, os.path
import ConfigParser
from optparse import OptionParser

import snap
from snapoptions import *
from snap.exceptions import *

class ConfigOptions:
    """Container holding all the configuration options available
       to the Snap system"""

    packagesystem=''
    mode=None
    verbose=False
    snapfile=DEFAULT_SNAPFILE
    snaphost=''
    handlefiles=False
    handlepackages=True
    include=''
    exclude=''

    BACKUP=0
    RESTORE=1

class Config:
    """Represents the snap config file to be read and parsed"""

    parser = None

    def __init__(self, file):
        '''
        Initialize the config file, specifying its path

        @param file - the path to the file to load
        '''

        self.parser = ConfigParser.ConfigParser()
        self.parser.read(file)

    def get_bool(self, key, section = 'main'):
        '''
        Retreive the indicated boolean value from the config file

        @param key - the string key corresponding to the boolean value to retrieve
        @param section - the section to retrieve the value from
        @returns - the value or False if not found
        '''

        try:
            v = self.parser.get(section, key)
            if v == 'True' or v == 'true' or v == '1':
                return True
            elif v == 'False' or v == 'false' or v == '0':
                return False
        except:
            return False  # If not found, value is false

    def get_string(self, key, section = 'main'):
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

class ConfigManager:
    """The configuration manager, used to set and verify snap config values 
       from the config file and command line. Primary interface to the 
       Configuration System"""
    
    configoptions=None
    parser=None

    # read values from the config file and set them in the target ConfigOptions
    def read_config(self):
        debug('Parsing config')
        if not os.path.exists(CONFIG_FILE):
            snap.callback.snapcallback.error("Config file not found")
            raise SnapMissingFileError
        cfg = Config(CONFIG_FILE)
        if cfg.get_bool('restore'):
            self.configoptions.mode = Snap.RESTORE
        if cfg.get_bool('backup'):
            self.configoptions.mode = Snap.BACKUP
        if cfg.get_bool('verbose'):
            self.configoptions.verbose=True
        if cfg.get_bool('packages'):
            self.configoptions.handlepackages=True
        elif cfg.get_bool('nopackages'):
            self.configoptions.handlepackages=False
        if cfg.get_bool('files'):
            self.configoptions.handlefiles=True
        elif cfg.get_bool('nofiles'):
            self.configoptions.handlefiles=False
        sf = cfg.get_string('snapfile')
        sh = cfg.get_string('snaphost')
        inc = cfg.get_string('include')
        ex = cfg.get_string('exclude')
        ps = cfg.get_string('packagesystem')
        
        if sf != None:
            self.configoptions.snapfile = sf
        if sh != None:
            self.configoptions.snaphost = sh
        if inc != None:
            self.configoptions.include = inc
        if ex != None:
            self.configoptions.exclude = ex
        if ps != None:
            self.configoptions.packagesystem = ps

    # Setup the parser to expect the values when parsing the command line
    def _setup_options(self):
        debug("Setting up options")
        usage = "usage: %prog [options] arg"
        self.parser = OptionParser(usage, version=SNAP_VERSION)
        self.parser.add_option('', '--restore', dest = 'restore', action='store_true', default=False, help='Restore snapshot')
        self.parser.add_option('', '--backup', dest = 'backup', action='store_true', default=False, help='Take snapshot')
        self.parser.add_option('-v', '--verbose', dest = 'verbose', action='store_true', default=False, help='Verbose output')
        self.parser.add_option('-f', '--snapfile', dest = 'snapfile', action='store', default=None, help='Snapshot file')
        #self.parser.add_option('', '--snaphost', dest = 'snaphost', action='store', default=None, help='Snapshot host uri')
        self.parser.add_option('', '--packages', dest = 'packages', action='store_true', default=False, help='Include packages processing')
        self.parser.add_option('', '--nopackages', dest = 'nopackages', action='store_true', default=False, help='Exclude packages processing')
        self.parser.add_option('', '--files', dest = 'files', action='store_true', default=False, help='Include file processing')
        self.parser.add_option('', '--nofiles', dest = 'nofiles', action='store_true', default=False, help='Exclude file processing')
        self.parser.add_option('-i', '--include', dest = 'include', action='store', default=None, help='":" seperated Include paths')
        self.parser.add_option('-e', '--exclude', dest = 'exclude', action='store', default=None, help='":" seperated Exclude paths')

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
        #if options.snaphost != None:
            #self.configoptions.snaphost=options.snaphost
        if options.verbose:
            self.configoptions.verbose=True
        if options.snapfile != None:
            self.configoptions.snapfile=options.snapfile
        if options.packages:
            self.configoptions.handlepackages=True
        elif options.nopackages:
            self.configoptions.handlepackages=False
        if options.files:
            self.configoptions.handlefiles=True
        elif options.nofiles:
            self.configoptions.handlefiles=False
        if options.include != None:
            self.configoptions.include+= ':' + options.include
        if options.exclude != None:
            self.configoptions.exclude+=':' + options.exclude

    def verify_integrity(self):
        '''
        verify the integrity of the current option set

        @raises - SnapArgeError if the options are invalid
        '''

        debug('Verifying Options Intgerity')
        if self.configoptions.mode == None: # mode not specified
            snap.callback.snapcallback.error("Specify backup or restore")
            raise SnapArgError 
        if self.configoptions.mode == ConfigOptions.RESTORE and self.configoptions.snapfile == DEFAULT_SNAPFILE: # need to specify snapfile when restoring
            snap.callback.snapcallback.error("Specify snapfile")
            raise SnapArgError
        # Add any additional checks here

    def __init__(self, targetconfig):
        '''
        create the config manager 

        @param targetconfig - instance of ConfigOptions which to set values retrieved
                              from the config file and command line on
        '''

        self.configoptions=targetconfig
        self._setup_options()
