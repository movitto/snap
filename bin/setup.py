#!/usr/bin/python
#
# snap - a utility for system backup and restoration
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

from distutils.core import setup

setup(name = 'snap',
	version='0.1',
	description = 'system snapshotter and restoration utility',
	author = 'Mohammed Morsi',
	author_email = 'mmorsi@yahoo.com',
	url = 'http://morsi.org/projects/snap',
	packages = ['snap'],
	data_files = [("/etc", ["resources/snap.conf"]), 
			('/usr/share/snap/', ['resources/snap.glade']),
			("/usr/share/snap/packagesystems/", ['packagesystems/yumpackagesystem.py'])],
	scripts = ["bin/snaptool", "bin/gsnap"] )
