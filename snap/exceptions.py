#!/usr/bin/python
#
# exceptions which snap will raise
#
# (C) Copyright 2007 Mohammed Morsi (movitto@yahoo.com)
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

class SnapArgError(Exception):
    """An illegal arguement to the system was specified or an invalid 
       option set was detected in ConfigManager.verify_integrity()"""

    def __init__(self,value = ''):
        self.parameter=value
    def __str__(self):
        return repr(self.parameter)

class SnapFilesystemError(Exception):
    """An error occured during a filesystem operation"""

    def __init__(self,value = ''):
        self.parameter=value
    def __str__(self):
        return repr(self.parameter)

class SnapMissingFileError(SnapFilesystemError):
    """A required file was not found"""

    def __init__(self,value = ''):
        self.parameter=value
    def __str__(self):
        return repr(self.parameter)

class SnapMissingDirError(SnapFilesystemError):
    """A required directory was not found"""

    def __init__(self,value = ''):
        self.parameter=value
    def __str__(self):
        return repr(self.parameter)

class SnapPackageSystemError(Exception):
    """An error occured during a packagesystem operation"""

    def __init__(self,value = ''):
        self.parameter=value
    def __str__(self):
        return repr(self.parameter)

class SnapInsufficientPermissionError(Exception):
    """The user does not have permission to perform the requested operation"""

    def __init__(self,value = ''):
        self.parameter=value
    def __str__(self):
        return repr(self.parameter)
