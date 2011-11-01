#!/usr/bin/python
#
# Mock Postgresql service backup/restoration adapter
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

class Mock:

    mock_is_available = True

    is_available_called  = False
    install_prereqs_called = False
    backup_called  = False
    restore_called = False

    def is_available(self):
        """simply flag that this has been called"""
        Mock.is_available_called = True
        return Mock.mock_is_available

    def install_prereqs(self):
        """simply flag that this has been called"""
        Mock.install_prereqs_called = True

    def backup(self, basedir):
        """simply flag that backup has been called"""
        Mock.backup_called = True

    def restore(self, basedir):
        """simply flag that restore has been called"""
        Mock.restore_called = True
