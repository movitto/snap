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

from snap.filemanager import FileManager
from snap.options     import *

class OS:
  '''helper methods to perform OS level operations'''

  def lookup():
    '''lookup and return the current operating system we are running as'''
    # TODO other operating system checks
    if FileManager.exists('/etc/fedora-release'):
      return 'fedora'
    elif FileManager.exists('C:\\'):
      return 'windows'
    return None
  lookup=staticmethod(lookup)

  def default_backend_for_target(os, target):
    '''return the default backend configured for the given os / snapshot target'''
    return DEFAULT_BACKENDS[os][target]
  default_backend_for_target = staticmethod(default_backend_for_target)
