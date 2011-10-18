#!/usr/bin/python
#
# test/callback.py SnapCallbackBase implementation to be used by the testing system to catch and handle errors / warning
#
# Version: 0.1
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

from snap.callback import SnapCallbackBase

class TestSystemCallback(SnapCallbackBase):
    def error(self, error):
        pass
    def warn(self, warning):
        pass

