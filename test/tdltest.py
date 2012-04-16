#!/usr/bin/python
#
# test/tdltest.py unit test suite for snap.metadata.tdl
#
# (C) Copyright 2012 Mo Morsi (mo@morsi.org)
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
import unittest

from snap.exceptions  import MissingDirError
from snap.metadata.tdl import TDLFile

class TDLFileTest(unittest.TestCase):
    def testInvalidSnapdirectoryShouldRaiseError(self):
        with self.assertRaises(MissingDirError) as context:
            TDLFile('foo', '/invalid/dir')
        self.assertEqual(context.exception.message, '/invalid/dir is an invalid snap working directory ')

    def testWriteTDLFile(self):
        snapdir = os.path.join(os.path.dirname(__file__), "data")
        tdlfile = TDLFile(os.path.join(snapdir, "test.tdl"), snapdir)
        tdlfile.write()

        tf = open(os.path.join(snapdir, "test.tdl"), 'r')
        contents = tf.read()
        tf.close()

        # FIXME verify contents
