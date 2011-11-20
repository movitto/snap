#!/usr/bin/python
#
# test/servicedispatchtest.py unit test suite for the dispatch service backend
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
import re
import stat
import errno
import shutil
import fnmatch
import unittest
import subprocess

from snap.filemanager import FileManager
from snap.metadata.service import ServicesRecordFile
from snap.metadata.sfile import SFile
from snap.osregistry import OS
    
import snap.backends.services.dispatcher
import snap.backends.services.windowsdispatcher
import snap.backends.services.linuxdispatcher

import snap.backends.services.adapters.mock
import snap.backends.services.adapters.iptables
import snap.backends.services.adapters.postgresql
import snap.backends.services.adapters.mysql
import snap.backends.services.adapters.httpd
import snap.backends.services.adapters.iis

class ServiceDispatcherTest(unittest.TestCase):
    def setUp(self):
        self.basedir = os.path.join(os.path.dirname(__file__), "data", "basedir")
        if os.path.isdir(self.basedir):
            shutil.rmtree(self.basedir)
        os.mkdir(self.basedir)
        
        if OS.is_windows():
            self.dispatcher = snap.backends.services.windowsdispatcher.WindowsDispatcher()
        else:
            self.dispatcher = snap.backends.services.linuxdispatcher.LinuxDispatcher()

    def tearDown(self):
        shutil.rmtree(self.basedir)

    def testStartStopRunningService(self):
        if OS.is_windows():
            service = "WPCsvc" # windows parental controls
        else:
            service = snap.backends.services.adapters.httpd.Httpd.DAEMON
        is_running = self.dispatcher.service_running(service)
        self.dispatcher.start_service(service)
        self.assertTrue(self.dispatcher.service_running(service))
        self.dispatcher.stop_service(service)
        self.assertFalse(self.dispatcher.service_running(service))
        if is_running:
            self.dispatcher.start_service(service)

    def testLoadServices(self):
        services_path = os.path.join(os.path.dirname(__file__),
                                     "..", "snap", "backends", "services", "adapters")
        services = os.listdir(services_path)
        service_classes = []

        dispatcher = snap.backends.services.dispatcher.Dispatcher()

        for service in services:
            if service[0:8] != "__init__" and fnmatch.fnmatch(service, "*.py"):
                service = service.replace(".py", "")
                service_classes.append(dispatcher.load_service(service).__class__)

        # TODO for now just have services tested here statically set, perhaps a better way TODO this?
        self.assertIn(snap.backends.services.adapters.iptables.Iptables, service_classes)
        self.assertIn(snap.backends.services.adapters.postgresql.Postgresql, service_classes)
        self.assertIn(snap.backends.services.adapters.mysql.Mysql, service_classes)
        self.assertIn(snap.backends.services.adapters.mock.Mock, service_classes)

    def testDispatcherBackup(self):
        snap.backends.services.adapters.mock.Mock.mock_is_available = True
        snap.backends.services.adapters.mock.Mock.is_available_called = False
        snap.backends.services.adapters.mock.Mock.backup_called = False

        dispatcher = snap.backends.services.dispatcher.Dispatcher()
        dispatcher.backup(self.basedir, include=['mock'])

        self.assertTrue(snap.backends.services.adapters.mock.Mock.is_available_called)
        self.assertTrue(snap.backends.services.adapters.mock.Mock.backup_called)
        self.assertTrue(os.path.isfile(os.path.join(self.basedir, "services.xml")))

        record = ServicesRecordFile(os.path.join(self.basedir, "services.xml"))
        services = record.read()
        service_names = []
        for service in services:
            service_names.append(service.name)
        self.assertIn("mock", service_names)

    def testNoBackupIfNotAvailable(self):
        snap.backends.services.adapters.mock.Mock.mock_is_available = False
        snap.backends.services.adapters.mock.Mock.is_available_called = False
        snap.backends.services.adapters.mock.Mock.backup_called = False

        dispatcher = snap.backends.services.dispatcher.Dispatcher()
        dispatcher.backup(self.basedir, include=['mock'])

        self.assertTrue(snap.backends.services.adapters.mock.Mock.is_available_called)
        self.assertFalse(snap.backends.services.adapters.mock.Mock.backup_called)

    def testOSDispatcher(self):
        if OS.is_windows():
            self.assertEqual(snap.backends.services.dispatcher.Dispatcher.os_dispatcher(),
                             snap.backends.services.windowsdispatcher.WindowsDispatcher)
        elif OS.is_linux():
            self.assertEqual(snap.backends.services.dispatcher.Dispatcher.os_dispatcher(),
                             snap.backends.services.linuxdispatcher.LinuxDispatcher)

    def testDispatcherRestore(self):
        # first backup the mock service
        dispatcher = snap.backends.services.dispatcher.Dispatcher()
        dispatcher.backup(self.basedir, include=['mock'])

        snap.backends.services.adapters.mock.Mock.mock_is_available = True
        snap.backends.services.adapters.mock.Mock.is_available_called = False
        snap.backends.services.adapters.mock.Mock.install_prereqs_called = False
        snap.backends.services.adapters.mock.Mock.restore_called = False

        # then restore it
        dispatcher.restore(self.basedir)
        self.assertTrue(snap.backends.services.adapters.mock.Mock.is_available_called)
        self.assertFalse(snap.backends.services.adapters.mock.Mock.install_prereqs_called)
        self.assertTrue(snap.backends.services.adapters.mock.Mock.restore_called)
        
        # ensure not restored if prereqs is not avaiable
        snap.backends.services.adapters.mock.Mock.mock_is_available = False
        snap.backends.services.adapters.mock.Mock.restore_called = False
        dispatcher.restore(self.basedir)
        self.assertFalse(snap.backends.services.adapters.mock.Mock.restore_called)
        
    def testNoInstallPrereqsIfAvailable(self):
        snap.backends.services.adapters.mock.Mock.mock_is_available = True
        snap.backends.services.adapters.mock.Mock.is_available_called = False
        snap.backends.services.adapters.mock.Mock.install_prereqs_called = False
        snap.backends.services.adapters.mock.Mock.restore_called = False

        # first backup the mock service
        dispatcher = snap.backends.services.dispatcher.Dispatcher()
        dispatcher.backup(self.basedir, include=['mock'])

        # then restore it
        dispatcher.restore(self.basedir)
        self.assertTrue(snap.backends.services.adapters.mock.Mock.is_available_called)
        self.assertFalse(snap.backends.services.adapters.mock.Mock.install_prereqs_called)
        self.assertTrue(snap.backends.services.adapters.mock.Mock.restore_called)

    def testSetPostgresEnvPassword(self):
        self.assertEqual(snap.backends.services.adapters.postgresql.Postgresql.set_pgpassword_env()['PGPASSWORD'],
                         snap.config.options.service_options['postgresql_password'])
        
    def testPostgresqlDbExists(self):
        is_running = self.dispatcher.service_running('postgresql')
        self.dispatcher.start_service('postgresql')
        self.assertTrue(snap.backends.services.adapters.postgresql.Postgresql.db_exists('postgres'))
        self.assertFalse(snap.backends.services.adapters.postgresql.Postgresql.db_exists('non-existant-db'))
        if not is_running:
            self.dispatcher.stop_service('postgresql')

    def testPostgresqlCreateDropDb(self):
        is_running = self.dispatcher.service_running('postgresql')
        self.dispatcher.start_service('postgresql')
        snap.backends.services.adapters.postgresql.Postgresql.create_db('test_db')
        self.assertTrue(snap.backends.services.adapters.postgresql.Postgresql.db_exists('test_db'))
        snap.backends.services.adapters.postgresql.Postgresql.drop_db('test_db')
        self.assertFalse(snap.backends.services.adapters.postgresql.Postgresql.db_exists('test_db'))
        if not is_running:
            self.dispatcher.stop_service('postgresql')

    def testPostgresqlService(self):
        # first start the service if it isn't running
        already_running = self.dispatcher.service_running(snap.backends.services.adapters.postgresql.Postgresql.DAEMON)
        if not already_running:
            self.dispatcher.start_service(snap.backends.services.adapters.postgresql.Postgresql.DAEMON)

        # create a test database
        snap.backends.services.adapters.postgresql.Postgresql.create_db('snaptest')

        # restore to original state
        if not already_running:
            self.dispatcher.stop_service(snap.backends.services.adapters.postgresql.Postgresql.DAEMON)

        backend = snap.backends.services.adapters.postgresql.Postgresql()
        backend.backup(self.basedir)

        # ensure the process is in its original state
        currently_running = self.dispatcher.service_running(snap.backends.services.adapters.postgresql.Postgresql.DAEMON)
        self.assertEqual(already_running, currently_running)

        # assert the db dump exists and has the db dump
        self.assertTrue(os.path.isfile(self.basedir + "/dump.psql"))
        c = FileManager.read_file(self.basedir + "/dump.psql")
        self.assertEqual(1, len(re.findall('CREATE DATABASE snaptest', c)))

        # finally cleanup
        self.dispatcher.start_service(snap.backends.services.adapters.postgresql.Postgresql.DAEMON)
        snap.backends.services.adapters.postgresql.Postgresql.drop_db('snaptest')

        # stop the service, backup the datadir
        self.dispatcher.stop_service(snap.backends.services.adapters.postgresql.Postgresql.DAEMON)
        shutil.copytree(snap.backends.services.adapters.postgresql.Postgresql.DATADIR,
                        snap.backends.services.adapters.postgresql.Postgresql.DATADIR + ".bak")


        # test restore
        backend.restore(self.basedir)

        # ensure service is running, datadir has been initialized
        self.assertTrue(self.dispatcher.service_running(snap.backends.services.adapters.postgresql.Postgresql.DAEMON))
        self.assertTrue(os.path.isdir(snap.backends.services.adapters.postgresql.Postgresql.DATADIR))

        # ensure the db exists
        self.assertTrue(snap.backends.services.adapters.postgresql.Postgresql.db_exists('snaptest'))

        # stop the service, restore the db
        self.dispatcher.stop_service(snap.backends.services.adapters.postgresql.Postgresql.DAEMON)
        shutil.rmtree(snap.backends.services.adapters.postgresql.Postgresql.DATADIR)
        shutil.move(snap.backends.services.adapters.postgresql.Postgresql.DATADIR + ".bak",
                    snap.backends.services.adapters.postgresql.Postgresql.DATADIR)
        
        # XXX dirty hack make sure the datadir is owned by postgres
        data_dir = None
        if snap.osregistry.OS.yum_based():
            data_dir = snap.backends.services.adapters.postgresql.Postgresql.DATADIR + "/../"
        elif snap.osregistry.OS.apt_based():
            data_dir = snap.backends.services.adapters.postgresql.Postgresql.DATADIR + "/../../"
        elif snap.osregistry.OS.is_windows():
            data_dir = snap.backends.services.adapters.postgresql.Postgresql.DATADIR
        snap.osregistry.OSUtils.chown(data_dir, username='postgres')
        
        # cleanup, restore to original state
        if already_running:
            self.dispatcher.start_service(snap.backends.services.adapters.postgresql.Postgresql.DAEMON)


    def testMysqlDbExists(self):
        is_running = self.dispatcher.service_running(snap.backends.services.adapters.mysql.Mysql.DAEMON)
        self.dispatcher.start_service(snap.backends.services.adapters.mysql.Mysql.DAEMON)
        self.assertTrue(snap.backends.services.adapters.mysql.Mysql.db_exists('mysql'))
        self.assertFalse(snap.backends.services.adapters.mysql.Mysql.db_exists('non-existant-db'))
        if not is_running:
            self.dispatcher.stop_service(snap.backends.services.adapters.mysql.Mysql.DAEMON)

    def testMysqlCreateDropDb(self):
        is_running = self.dispatcher.service_running(snap.backends.services.adapters.mysql.Mysql.DAEMON)
        self.dispatcher.start_service(snap.backends.services.adapters.mysql.Mysql.DAEMON)
        snap.backends.services.adapters.mysql.Mysql.create_db('snap_test_db')
        self.assertTrue(snap.backends.services.adapters.mysql.Mysql.db_exists('snap_test_db'))
        snap.backends.services.adapters.mysql.Mysql.drop_db('snap_test_db')
        self.assertFalse(snap.backends.services.adapters.mysql.Mysql.db_exists('snap_test_db'))
        if not is_running:
            self.dispatcher.stop_service(snap.backends.services.adapters.mysql.Mysql.DAEMON)

    def testMysqlService(self):
        # first start the service if it isn't running
        already_running = self.dispatcher.service_running(snap.backends.services.adapters.mysql.Mysql.DAEMON)
        if not already_running:
            self.dispatcher.start_service(snap.backends.services.adapters.mysql.Mysql.DAEMON)

        # create a test database
        snap.backends.services.adapters.mysql.Mysql.create_db('snaptest')

        # restore to original state
        if not already_running:
            self.dispatcher.stop_service(snap.backends.services.adapters.mysql.Mysql.DAEMON)

        backend = snap.backends.services.adapters.mysql.Mysql()
        backend.backup(self.basedir)

        # ensure the process is in its original state
        currently_running = self.dispatcher.service_running(snap.backends.services.adapters.mysql.Mysql.DAEMON)
        self.assertEqual(already_running, currently_running)

        # assert the db dump exists and has the db dump
        self.assertTrue(os.path.isfile(self.basedir + "/dump.mysql"))
        c = FileManager.read_file(self.basedir + "/dump.mysql")
        self.assertEqual(1, len(re.findall('CREATE DATABASE.*snaptest', c)))

        # finally cleanup
        self.dispatcher.start_service(snap.backends.services.adapters.mysql.Mysql.DAEMON)
        snap.backends.services.adapters.mysql.Mysql.drop_db('snaptest')

        # stop the service, backup the datadir
        self.dispatcher.stop_service(snap.backends.services.adapters.mysql.Mysql.DAEMON)
        shutil.copytree(snap.backends.services.adapters.mysql.Mysql.DATADIR,
                        snap.backends.services.adapters.mysql.Mysql.DATADIR + ".bak")

        # test restore
        backend.restore(self.basedir)

        # ensure service is running, datadir has been initialized
        self.assertTrue(self.dispatcher.service_running(snap.backends.services.adapters.mysql.Mysql.DAEMON))
        self.assertTrue(os.path.isdir(snap.backends.services.adapters.mysql.Mysql.DATADIR))

        # ensure the db exists
        self.assertTrue(snap.backends.services.adapters.mysql.Mysql.db_exists('snaptest'))

        # stop the service, restore the db
        self.dispatcher.stop_service(snap.backends.services.adapters.mysql.Mysql.DAEMON)
        shutil.rmtree(snap.backends.services.adapters.mysql.Mysql.DATADIR)
        shutil.move(snap.backends.services.adapters.mysql.Mysql.DATADIR + ".bak",
                    snap.backends.services.adapters.mysql.Mysql.DATADIR)
        
        # XXX dirty hack make sure the datadir is owned by mysql
        data_dir = None
        if snap.osregistry.OS.yum_based():
            data_dir = snap.backends.services.adapters.postgresql.Postgresql.DATADIR + "/../"
        elif snap.osregistry.OS.apt_based():
            data_dir = snap.backends.services.adapters.postgresql.Postgresql.DATADIR + "/../../"
        elif snap.osregistry.OS.is_windows():
            data_dir = snap.backends.services.adapters.postgresql.Postgresql.DATADIR
        snap.osregistry.OSUtils.chown(data_dir, username='mysql')

        # cleanup, restore to original state
        if already_running:
            self.dispatcher.start_service(snap.backends.services.adapters.mysql.Mysql.DAEMON)


    @unittest.skipIf(OS.is_windows(), "windows doesn't support iptables")
    def testIptablesService(self):        
        # manually backup iptalbes to restore after the test
        f = file(self.basedir + "/iptables-backup", 'w')
        popen = subprocess.Popen("iptables-save", stdout=f)
        popen.wait()
        self.assertEqual(0, popen.returncode)

        # flush the filter table (removes all rules)
        popen = subprocess.Popen(["iptables", "-F"])
        popen.wait()
        self.assertEqual(0, popen.returncode)

        # allow port 22 traffic
        popen = subprocess.Popen(["iptables", "-A", "INPUT", "-p", "tcp", "--dport", "22", "-j", "ACCEPT"])
        popen.wait()
        self.assertEqual(0, popen.returncode)

        # perform the backup
        backend = snap.backends.services.adapters.iptables.Iptables()
        backend.backup(self.basedir)

        # assert we have our rule
        self.assertTrue(os.path.isfile(self.basedir + "/iptables.rules"))
        c = FileManager.read_file(self.basedir + "/iptables.rules")
        self.assertEqual(1, len(re.findall('-A INPUT -p tcp -m tcp --dport 22 -j ACCEP', c)))

        # again flush the filter table
        popen = subprocess.Popen(["iptables", "-F"])
        popen.wait()
        self.assertEqual(0, popen.returncode)

        # perform the restoration
        backend.restore(self.basedir)

        # assert that we have registered port 22
        f = file(self.basedir + "/iptables-running", 'w')
        popen = subprocess.Popen(["iptables", "-nvL"], stdout=f)
        popen.wait()
        self.assertEqual(0, popen.returncode)
        c = re.sub("\s+", " ", FileManager.read_file(self.basedir + "/iptables-running"))
        self.assertEqual(1,
          len(re.findall("ACCEPT.*tcp dpt:22", c))) # TODO prolly could be a better regex
          

        # finally fiush the chain one last time and restore the original rules
        popen = subprocess.Popen(["iptables", "-F"])
        popen.wait()
        self.assertEqual(0, popen.returncode)
        popen = subprocess.Popen(["iptables-restore", self.basedir + "/iptables-backup"])
        popen.wait()
        self.assertEqual(0, popen.returncode)

    def testHttpdService(self):
        # backup the http conf directory and document roots
        test_backup_dir = os.path.join(self.basedir, "snap-http-test")
        if os.path.isdir(test_backup_dir):
            shutil.rmtree(test_backup_dir)
        shutil.copytree(snap.backends.services.adapters.httpd.Httpd.CONF_D,
                        os.path.join(test_backup_dir, "conf_d"))
        shutil.copytree(snap.backends.services.adapters.httpd.Httpd.DOCUMENT_ROOT,
                        os.path.join(test_backup_dir, "doc_root"))

        # run the backup
        test_base_dir = os.path.join(self.basedir, "snap-http-basedir")
        backend = snap.backends.services.adapters.httpd.Httpd()
        backend.backup(test_base_dir)

        # ensure conf.d and document root were backed up
        bfiles = []
        for root, dirs, files in os.walk(snap.backends.services.adapters.httpd.Httpd.CONF_D):
            for hfile in files:
                rfile = os.path.join(root, hfile)
                ffile = os.path.join(test_base_dir, rfile)
                self.assertTrue(os.path.isfile(ffile))
                bfiles.append(os.path.join(root, hfile))
        for root, dirs, files in os.walk(snap.backends.services.adapters.httpd.Httpd.DOCUMENT_ROOT):
            for hfile in files:
                rfile = os.path.join(root, hfile)
                ffile = os.path.join(test_base_dir, rfile)
                self.assertTrue(os.path.isfile(ffile))
                bfiles.append(os.path.join(root, hfile))
        self.assertTrue(os.path.isfile(os.path.join(test_base_dir, "service-http.xml")))

        # run the restore
        shutil.rmtree(snap.backends.services.adapters.httpd.Httpd.CONF_D)
        shutil.rmtree(snap.backends.services.adapters.httpd.Httpd.DOCUMENT_ROOT)
        backend.restore(test_base_dir)

        # ensure the files backed up were restored
        for hfile in bfiles:
            self.assertTrue(os.path.isfile(hfile))

        # ensure the service is running
        self.assertTrue(self.dispatcher.service_running(snap.backends.services.adapters.httpd.Httpd.DAEMON))

        # restore backup
        shutil.rmtree(snap.backends.services.adapters.httpd.Httpd.CONF_D)
        shutil.rmtree(snap.backends.services.adapters.httpd.Httpd.DOCUMENT_ROOT)
        shutil.copytree(os.path.join(test_backup_dir, "conf_d"),
                        snap.backends.services.adapters.httpd.Httpd.CONF_D)
        shutil.copytree(os.path.join(test_backup_dir, "doc_root"),
                        snap.backends.services.adapters.httpd.Httpd.DOCUMENT_ROOT)
        shutil.rmtree(test_backup_dir)

    @unittest.skipUnless(OS.is_windows(), "only windows support IIS")
    def testIisService(self):
        # backup the iis conf directory and document roots
        test_backup_dir = os.path.join(self.basedir, "snap-iis-test")
        if os.path.isdir(test_backup_dir):
            shutil.rmtree(test_backup_dir)
        shutil.copytree(snap.backends.services.adapters.iis.Iis.CONFIG_ROOT,
                        os.path.join(test_backup_dir, "conf"))

        # run the backup
        test_base_dir = os.path.join(self.basedir, "snap-iis-basedir")
        backend = snap.backends.services.adapters.iis.Iis()
        backend.backup(test_base_dir)

        # ensure conf.d and document root were backed up
        bfiles = []
        for root, dirs, files in os.walk(snap.backends.services.adapters.iis.Iis.CONFIG_ROOT):
            for hfile in files:
                rfile = os.path.join(root, hfile)
                ffile = os.path.join(test_base_dir, rfile)
                self.assertTrue(os.path.isfile(ffile))
                bfiles.append(os.path.join(root, hfile))
        self.assertTrue(os.path.isfile(os.path.join(test_base_dir, "service-iis.xml")))

        # run the restore
        shutil.rmtree(snap.backends.services.adapters.iis.Iis.CONFIG_ROOT, ignore_errors=True)
        backend.restore(test_base_dir)

        # ensure the files backed up were restored
        for hfile in bfiles:
            self.assertTrue(os.path.isfile(hfile))

        # ensure the features are enabled
        self.assertTrue(snap.backends.services.windowsdispatcher.WindowsDispatcher.is_feature_enabled(snap.backends.services.adapters.iis.Iis.WEBSERVER_FEATURE))

        # restore backup
        shutil.rmtree(snap.backends.services.adapters.iis.Iis.CONFIG_ROOT, ignore_errors=True)
        for root, dirs, files in os.walk(os.path.join(test_backup_dir, "conf")):
            for idir  in dirs:
                fdir = os.path.join(snap.backends.services.adapters.iis.Iis.CONFIG_ROOT, idir)
                if not os.path.isdir(fdir):
                    os.makedirs(fdir)
            for ifile in files:
                sfile = os.path.join(root, ifile)
                
                ffile = os.path.join(snap.backends.services.adapters.iis.Iis.CONFIG_ROOT, ifile)
                if not os.path.isfile(ffile):
                    shutil.copy(os.path.join(root, ifile), ffile)
                os.chmod(sfile, stat.S_IWRITE)
                os.remove(sfile)
        for bfile in bfiles:
            fbfile = os.path.join(test_base_dir, SFile.windows_path_escape(bfile))
            os.chmod(fbfile, stat.S_IWRITE)
            os.remove(fbfile)
        shutil.rmtree(test_backup_dir)
