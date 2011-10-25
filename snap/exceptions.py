#!/usr/bin/python
#
# exceptions which snap will raise
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

class SnapError(BaseException):
    """An error occured during Snap!'s operation"""

    def __init__(self,message = ''):
        BaseException.__init__(self, message)

class ArgError(SnapError):
    """An illegal arguement to the system was specified or an invalid 
       option set was detected in ConfigManager.verify_integrity()"""

    def __init__(self,message = ''):
        SnapError.__init__(self, message)

class FilesystemError(SnapError):
    """An error occured during a filesystem operation"""

    def __init__(self,message = ''):
        SnapError.__init__(self, message)

class MissingFileError(FilesystemError):
    """A required file was not found"""

    def __init__(self,message = ''):
        FilesystemError.__init__(self, message)

class MissingDirError(FilesystemError):
    """A required directory was not found"""

    def __init__(self,message = ''):
        FilesystemError.__init__(self, message)

class PackageSystemError(SnapError):
    """An error occured during a packagesystem operation"""

    def __init__(self,message = ''):
        SnapError.__init__(self, message)

class InsufficientPermissionError(SnapError):
    """The user does not have permission to perform the requested operation"""

    def __init__(self,message = ''):
        SnapError.__init__(self, message)
