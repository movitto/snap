#!/usr/bin/python
#
# test/configtest.py unit test suite for snap.config
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

import snap
import snap.config

class ConfigTest(unittest.TestCase):
    def testLogLevelAtLeast(self):
        orig_log_level = snap.config.options.log_level

        snap.config.options.log_level = 'quiet'
        self.assertTrue(snap.config.options.log_level_at_least('quiet'))
        self.assertFalse(snap.config.options.log_level_at_least('normal'))
        self.assertFalse(snap.config.options.log_level_at_least('verbose'))
        self.assertFalse(snap.config.options.log_level_at_least('debug'))

        snap.config.options.log_level = 'normal'
        self.assertTrue(snap.config.options.log_level_at_least('quiet'))
        self.assertTrue(snap.config.options.log_level_at_least('normal'))
        self.assertFalse(snap.config.options.log_level_at_least('verbose'))
        self.assertFalse(snap.config.options.log_level_at_least('debug'))

        snap.config.options.log_level = 'verbose'
        self.assertTrue(snap.config.options.log_level_at_least('quiet'))
        self.assertTrue(snap.config.options.log_level_at_least('normal'))
        self.assertTrue(snap.config.options.log_level_at_least('verbose'))
        self.assertFalse(snap.config.options.log_level_at_least('debug'))

        snap.config.options.log_level = 'debug'
        self.assertTrue(snap.config.options.log_level_at_least('quiet'))
        self.assertTrue(snap.config.options.log_level_at_least('normal'))
        self.assertTrue(snap.config.options.log_level_at_least('verbose'))
        self.assertTrue(snap.config.options.log_level_at_least('debug'))

        snap.config.options.log_level = orig_log_level
        pass

    def testWarnIfInvalidConfig(self):
        snap.callback.snapcallback.clear()
        snap.config.options.log_level = 'verbose'
        config_file = snap.config.ConfigFile('/some/invalid/path')
        self.assertIn("Config file /some/invalid/path not found", snap.callback.snapcallback.warnings)
        snap.callback.snapcallback.clear()
        pass

    def testStringToBool(self):
        self.assertTrue(snap.config.ConfigFile.string_to_bool("True"))
        self.assertTrue(snap.config.ConfigFile.string_to_bool("true"))
        self.assertTrue(snap.config.ConfigFile.string_to_bool("1"))
        self.assertFalse(snap.config.ConfigFile.string_to_bool("False"))
        self.assertFalse(snap.config.ConfigFile.string_to_bool("false"))
        self.assertFalse(snap.config.ConfigFile.string_to_bool("0"))
        self.assertEqual(None, snap.config.ConfigFile.string_to_bool(""))
        pass

    def testStringToArray(self):
        self.assertEqual(['foo', 'bar'], snap.config.ConfigFile.string_to_array("foo:bar"))
        pass

    def testParseConfigFile(self):
        config_file_path = os.path.join(os.path.dirname(__file__), "data/config-test.snap.conf")
        config_file = snap.config.ConfigFile(config_file_path)

        self.assertTrue(snap.config.options.target_backends['repos'])
        self.assertFalse(snap.config.options.target_backends['packages'])
        self.assertTrue(snap.config.options.target_backends['files'])
        self.assertFalse(snap.config.options.target_backends['services'])
        self.assertIn('/home', snap.config.options.target_includes['files'])
        self.assertIn('/etc', snap.config.options.target_includes['files'])
        self.assertNotIn('!/home/mmorsi', snap.config.options.target_includes['files'])
        self.assertIn('/home/mmorsi', snap.config.options.target_excludes['files'])

        self.assertEqual('tdl', snap.config.options.outputformat)
        self.assertEqual('/tmp/test-snap-shot', snap.config.options.snapfile)
        self.assertEqual('quiet', snap.config.options.log_level)
        self.assertEqual('foobar', snap.config.options.encryption_password)
        
        self.assertIn("postgresql_password", snap.config.options.service_options.keys())
        self.assertEqual("postgres", snap.config.options.service_options["postgresql_password"])
        self.assertIn("mysql_password", snap.config.options.service_options.keys())
        self.assertEqual("mysql", snap.config.options.service_options["mysql_password"])
        pass

    def testValidateMode(self):
        # ensure that if mode is not set, exception is thrown
        config = snap.config.Config()
        with self.assertRaises(snap.exceptions.ArgError) as context:
            config.verify_integrity()
        self.assertEqual(context.exception.message, 'Must specify backup or restore')
        pass

    def testValidateOutputFormat(self):
        # ensure that if outputformat is not specified, exception is thrown
        snap.config.options.mode = snap.config.ConfigOptions.BACKUP
        snap.config.options.outputformat = None
        config = snap.config.Config()
        with self.assertRaises(snap.exceptions.ArgError) as context:
            config.verify_integrity()
        self.assertEqual(context.exception.message, 'Must specify valid output format')
        pass

    def testValidateRestoreSnapFile(self):
        # ensure that if snapfile is not set, error is thrown
        snap.config.options.mode = snap.config.ConfigOptions.RESTORE
        snap.config.options.snapfile = None
        config = snap.config.Config()
        with self.assertRaises(snap.exceptions.ArgError) as context:
            config.verify_integrity()
        self.assertEqual(context.exception.message, 'Must specify snapfile')
        pass
