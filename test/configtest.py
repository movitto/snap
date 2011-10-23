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

import unittest

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
        config_file = snap.config.ConfigFile('/some/invalid/path')
        self.assertIn("Config file /some/invalid/path not found", snap.callback.snapcallback.warnings)
        snap.callback.snapcallback.clear()
        pass

    def testStringToBool(self):
        config_file = snap.config.ConfigFile('/some/invalid/path')
        self.assertTrue(config_file.__string_to_bool("True"))
        self.assertTrue(config_file.__string_to_bool("true"))
        self.assertTrue(config_file.__string_to_bool("1"))
        self.assertFalse(config_file.__string_to_bool("False"))
        self.assertFalse(config_file.__string_to_bool("false"))
        self.assertFalse(config_file.__string_to_bool("0"))
        self.assertEqual(None, config_file.__string_to_bool(""))
        snap.callback.snapcallback.clear()
        pass

    def testStringToArray(self):
        config_file = snap.config.ConfigFile('/some/invalid/path')
        self.assertEqual(['foo', 'bar'], config_file.__string_to_array("foo:bar"))
        snap.callback.snapcallback.clear()
        pass

    def testParseConfigFile(self):
        config_file_path = os.path.join(os.path.dirname(__file__), "data/config-test.snap.conf")
        config_file = snap.config.ConfigFile(config_file_path)

        self.assertTrue(self.config.options.target_backends['repos'])
        self.assertFalse(self.config.options.target_backends['packages'])
        self.assertTrue(self.config.options.target_backends['files'])
        self.assertFalse(self.config.options.target_backends['services'])
        self.assertIn('/home', self.config.options.target_includes['files'])
        self.assertIn('/etc', self.config.options.target_includes['files'])
        self.assertNotIn('!/home/mmorsi', self.config.options.target_includes['files'])
        self.assertIn('/home/mmorsi', self.config.options.target_excludes['files'])

        self.assertEqual('/tmp/test-snap-shot', snap.config.options.snapfile)
        self.assertEqual('quiet', snap.config.options.log_level)
        pass

    def testValidateMode(self):
        # ensure that if mode is not set, exception is thrown
        config = snap.config.Config()
        with self.assertRaises(snap.exceptions.ArgError) as context:
            config.verify_integrity()
        self.assertEqual(context.exception.message, 'Must specify backup or restore')
        pass

    def testValidateRestoreSnapFile(self):
        # ensure that if snap is in restore mode and snapfile
        # is not set, error is thrown
        snap.config.options.mode = snap.config.ConfigOptions.RESTORE
        config = snap.config.Config()
        with self.assertRaises(snap.exceptions.ArgError) as context:
            config.verify_integrity()
        self.assertEqual(context.exception.message, 'Must specify snapfile')
        pass
