#!/usr/bin/python
#
# snap - a utility for system backup and restoration
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
from distutils.core import setup

backends=[]
for root,dirs,files in os.walk("snap/backends"):
  module = root.replace('/', '.')
  for d in dirs:
    backends.append(module + "." + d)

setup(name = 'snap',
	version='0.5',
	description = 'system snapshotter and restoration utility',
	author = 'Mo Morsi',
	author_email = 'mo@morsi.org',
	url = 'http://morsi.org/projects/snap',
	packages = ['snap', "snap.metadata", "snap.backends"] + backends,
	data_files = [("/etc", ["resources/snap.conf"]), 
			('/usr/share/snap/', ['resources/snap-redux.glade', 'resources/snap.png'])],
	scripts = ["bin/snaptool", "bin/gsnap"] )
