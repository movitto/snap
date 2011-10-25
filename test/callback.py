#!/usr/bin/python
#
# test/callback.py SnapCallbackBase implementation to be used by the testing system to catch and handle errors / warning
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

import snap.callback

class TestSystemCallback(snap.callback.Callback):
    def __init__(self):
        self.clear()

    def clear(self):
        self.messages = []
        self.errors   = []
        self.warnings = []

    def message(self, msg):
        self.messages.append(msg)

    def error(self, error):
        self.errors.append(error)

    def warn(self, warning):
        self.warnings.append(warning)

snap.callback.snapcallback=TestSystemCallback()
