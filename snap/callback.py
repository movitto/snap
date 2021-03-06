# base interface for snap callback system
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
#

class Callback:
    """Base callback interface through which snap informs clients of progress"""
    
    def message(self, msg):
        '''
        a generic message

        @param - the string message
        '''
        pass

    def warn(self, warning):
        '''
        a non-critical warning

        @param - the string warning
        '''
        pass

    def error(self, error):
        '''
        critical error, program will terminate

        @param - the string error
        '''
        pass

# assign this to your SnapCallbackBase-derived callback to hookup the callback system
snapcallback=Callback()
