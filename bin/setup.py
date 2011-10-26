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

from distutils.core import setup

setup(name = 'snap',
	version='0.5',
	description = 'system snapshotter and restoration utility',
	author = 'Mo Morsi',
	author_email = 'mo@morsi.org',
	url = 'http://morsi.org/projects/snap',
	packages = ['snap'],
	data_files = [("/etc", ["resources/snap.conf"]), 
			('/usr/share/snap/', ['resources/snap.glade'])],
	scripts = ["bin/snaptool", "bin/gsnap"] )
