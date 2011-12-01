# Methods to dispatch service backup/restore operations to specific handlers
#   on windows systems
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

import re
import time
import tempfile
import subprocess

from snap.osregistry import OSUtils
from snap.backends.services.dispatcher import Dispatcher

class WindowsDispatcher(Dispatcher):
    '''implements the snap! services target backend, dispatching to handlers '''

    # XXX hack service may not yet be started/stopped after the sc command
    #  so we use a number of tries to wait for it
    SERVICE_QUERY_TRIES = 5
    SERVICE_QUERY_DELAY = 1

    def service_running(service):
        '''helper to return boolean indicating if the specified service is running'''
        for i in range(WindowsDispatcher.SERVICE_QUERY_TRIES):
            out = open(OSUtils.null_file(), 'w')
            popen = subprocess.Popen(["sc", "query", service], stdout=subprocess.PIPE, stderr=out)
            popen.wait()
            output = popen.stdout.read()
            if re.search(".*STATE.*PENDING", output):
                time.sleep(WindowsDispatcher.SERVICE_QUERY_DELAY)
                break
        if re.search(".*STATE.*RUNNING.*", output):
            return True
        return False
    service_running = staticmethod(service_running)

    def start_service(service):
        '''helper to start the specified service
        
        @returns boolean indicating if service was started or not'''
        out = open(OSUtils.null_file(), 'w')
        popen = subprocess.Popen(["sc", "start", service],
                                 stdout=out, stderr=out)
        popen.wait()
        time.sleep(WindowsDispatcher.SERVICE_QUERY_DELAY)
        return WindowsDispatcher.service_running(service)
    start_service = staticmethod(start_service)

    def stop_service(service):
        '''helper to stop the specified service
        
        @returns boolean indicating if service was stopped or not'''
        out = open(OSUtils.null_file(), 'w')
        popen = subprocess.Popen(["sc", "stop", service], stdout=out, stderr=out)
        popen.wait()
        time.sleep(WindowsDispatcher.SERVICE_QUERY_DELAY)
        return not WindowsDispatcher.service_running(service)
    stop_service = staticmethod(stop_service)
    
    def get_features(matching_pattern=".*"):
        '''helper to return list of features, optionally matching specified pattern
        
        @param matching_pattern - pattern to match features against'''
        out = open(OSUtils.null_file(), 'w')
        features = []
        tfile = tempfile.TemporaryFile()
        popen = subprocess.Popen(["dism", "/online", "/Get-features"],
                                 stdout=tfile, stderr=out)
        popen.wait()
        
        tfile.seek(0)
        c = tfile.read()
        for f in re.findall(matching_pattern, c):
            features.append(f)
        return features
    get_features = staticmethod(get_features)
    
    def is_feature_enabled(feature):
        '''helper to return true/false pertaining to whether or not feature is enabled'''
        out = open(OSUtils.null_file(), 'w')
        tfile = tempfile.TemporaryFile()
        popen = subprocess.Popen(['dism', '/online', '/Get-FeatureInfo', '/featurename:' + feature],
                                 stdout=tfile, stderr=out)
        popen.wait()
        tfile.seek(0)
        c = tfile.read()
        m = re.search('State\s*:\s*([^\s]*)\s*', c)
        return m != None and m.group(1) == "Enabled"
    is_feature_enabled = staticmethod(is_feature_enabled)
    
    def enable_feature(feature):
        '''helper to enable the specified feature'''
        out = open(OSUtils.null_file(), 'w')
        popen = subprocess.Popen(["dism", "/online", "/enable-feature", "/featurename:" + feature, "/norestart"],
                                 stdout=out, stderr=out)
        popen.wait()
    enable_feature = staticmethod(enable_feature)
    
    def enable_features(features=[]):
        '''helper to enable list of features'''
        for feature in features:
            WindowsDispatcher.enable_feature(feature)
    enable_features = staticmethod(enable_features)
        
    def disable_feature(feature):
        '''helper to disable the specified feature'''
        out = open(OSUtils.null_file(), 'w')
        popen = subprocess.Popen(["dism", "/online", "/disable-feature", "/featurename:" + feature, "/norestart"],
                                 stdout=out, stderr=out)
        popen.wait()
    disable_feature = staticmethod(disable_feature)
    
    def disable_features(features=[]):
        '''helper to disable list of features'''
        for feature in features:
            WindowsDispatcher.disable_feature(feature)
    disable_features = staticmethod(disable_features)
