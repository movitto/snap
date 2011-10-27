#!/usr/bin/python
#
# test/cryptotest.py unit test suite for snap.crypto
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
import unittest

from snap.crypto import Crypto

class CryptoTest(unittest.TestCase):
    # TODO
    #def testGenerateKey(self):

    def testEncryptDecrypt(self):
        temp_file_path = os.path.join(os.path.dirname(__file__), "data/cfile")
        f = open(temp_file_path, 'w')
        f.write("foobar")
        f.close()

        key = Crypto.generate_key("secret_key")

        Crypto.encrypt_file(key, temp_file_path)
        self.assertTrue(os.path.exists(temp_file_path + ".enc"))

        f = open(temp_file_path + ".enc")
        contents = f.read()
        f.close()

        # TODO should do a better verification that it's actually encrypted properly
        self.assertTrue(contents != "foobar")

        os.remove(temp_file_path)
        Crypto.decrypt_file(key, temp_file_path + ".enc")

        f = open(temp_file_path)
        contents = f.read()
        f.close()

        self.assertTrue(contents == "foobar")

        os.remove(temp_file_path)
        os.remove(temp_file_path + ".enc")
