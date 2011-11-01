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

import re

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
      return operating_system in ['fedora', 'rhel', 'centos', 'ubuntu', 'debian']
  is_linux=staticmethod(is_linux)

  def apt_based(operating_system=None):
      '''return true if we're running an apt based system'''
      if operating_system == None:
          operating_system = OS.current_os
      return operating_system in ['ubuntu', 'debian']
  apt_based=staticmethod(apt_based)

  def yum_based(operating_system=None):
      '''return true if we're running an yum based system'''
      if operating_system == None:
          operating_system = OS.current_os
      return operating_system in ['fedora', 'rhel', 'centos']
  yum_based=staticmethod(yum_based)

  def default_backend_for_target(target, operating_system=None):
      '''return the default backend configured for the given os / snapshot target'''
      if operating_system == None:
          operating_system = OS.current_os
      return DEFAULT_BACKENDS[operating_system][target]
  default_backend_for_target = staticmethod(default_backend_for_target)
