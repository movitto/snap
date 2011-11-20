#!/usr/bin/python
#
# High level OS helpers
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
import re
import subprocess

from snap.filemanager import FileManager
from snap.options     import *

def lookup():
  '''lookup and return the current operating system we are running as'''

  # TODO other operating system checks
  if FileManager.exists('/etc/fedora-release'):
    return 'fedora'

  elif FileManager.exists('/etc/redhat-release'):
    return 'rhel'

  elif FileManager.exists('/etc/centos-release'):
    return 'centos'

  elif FileManager.exists("/proc/version"):
      c = FileManager.read_file("/proc/version")
      if len(re.findall('Ubuntu', c)) > 0:
          return 'ubuntu'
      elif len(re.findall('Debian', c)) > 0:
          return 'debian'

  elif FileManager.exists('C:\\'):
    return 'windows'

  return None

class OS:
  '''helper methods to perform OS level operations'''

  current_os = lookup()

  def is_linux(operating_system=None):
      '''return true if we're running a linux system'''
      if operating_system == None:
          operating_system = OS.current_os
      return operating_system in ['fedora', 'rhel', 'centos', 'ubuntu', 'debian', 'mock']
  is_linux = staticmethod(is_linux)
  
  def is_windows(operating_system=None):
      '''return true if we're running an apt based system'''
      if operating_system == None:
          operating_system = OS.current_os
      return operating_system in ['windows', 'mock_windows']
  is_windows = staticmethod(is_windows)

  def apt_based(operating_system=None):
      '''return true if we're running an apt based system'''
      if operating_system == None:
          operating_system = OS.current_os
      return operating_system in ['ubuntu', 'debian']
  apt_based = staticmethod(apt_based)

  def yum_based(operating_system=None):
      '''return true if we're running an yum based system'''
      if operating_system == None:
          operating_system = OS.current_os
      return operating_system in ['fedora', 'rhel', 'centos']
  yum_based = staticmethod(yum_based)
  
  def get_root(operating_system=None):
      '''return the root directory for the specified os'''
      return 'C:\\' if OS.is_windows(operating_system) else '/'
  get_root = staticmethod(get_root)
  
  def get_path_seperator(operating_system=None):
      return '\\' if OS.is_windows(operating_system) else '/'
  get_path_seperator = staticmethod(get_path_seperator)

  def default_backend_for_target(target, operating_system=None):
      '''return the default backend configured for the given os / snapshot target'''
      if operating_system == None:
          operating_system = OS.current_os
      return DEFAULT_BACKENDS[operating_system][target]
  default_backend_for_target = staticmethod(default_backend_for_target)

class OSUtils:

    def null_file():
        if OS.is_windows():
            return 'nul'
        else:
            return '/dev/null'
    null_file = staticmethod(null_file)

    def chown(cfile, uid=None, gid=None, username=None):
        if os.path.isdir(cfile):
            for f in os.listdir(cfile):
                OSUtils.chown(os.path.join(cfile, f),
                              uid=uid, gid=gid, username=username)
        
        if OS.is_windows() and username != None:
            # we don't actually change owner, just assign the user full permissions
            null_file = open(OSUtils.null_file(), 'w')
            popen = subprocess.Popen(["icacls", cfile, "/grant:r", username + ":F"],
                                     stdout=null_file, stderr=null_file)
            popen.wait()
        elif OS.is_linux():
            if (uid == None or gid == None) and username != None:
                import pwd
                user = pwd.getpwnam(username)
                uid = user.pw_uid
                gid = user.pw_gid
            if uid != None and gid != None:
                os.chown(cfile, uid, gid)
    chown = staticmethod(chown)
    
    def is_superuser():
        if OS.is_windows():
            # checks if snap is running under elevated privileges 
            # Note this means more than running it as a user in the admin group. You must launch
            # snaptool, the snap gui, or the development environment (cmd terminal, eclipse, or other)
            # by right clicking the program and selecting 'run as administrator',
            # even if your user is marked as an admin in the windows users control panel
            
            # XXX hacky way of doing this, but simplest way I could find outside of using the win32 api
            try:
                file("C:\Windows\snap-check", "w")
            except IOError, e:
                return False
            
            # We also check to see if the current user is in the admin group
            user_name = os.environ["USERNAME"]            
            process = subprocess.Popen(["net", "localgroup", "administrators"], stdout=subprocess.PIPE)
            while True:
                line = process.stdout.readline()
                if not line:
                    return False
                if re.match("^.*" + user_name + ".*$", line):
                    return True
        else:
            return os.geteuid() == 0
    is_superuser = staticmethod(is_superuser)
