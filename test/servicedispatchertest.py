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
import pwd
import shutil
import fnmatch
import unittest
import subprocess

import snap
from snap.metadata.service import ServicesRecordFile
from snap.backends.services.dispatcher import Dispatcher

import snap.backends.services.adapters.iptables
import snap.backends.services.adapters.postgresql
import snap.backends.services.adapters.mysql

class ServiceDispatcherTest(unittest.TestCase):
    def setUp(self):
        self.basedir = os.path.join(os.path.dirname(__file__), "data/basedir")
        if os.path.isdir(self.basedir):
            shutil.rmtree(self.basedir)
        os.mkdir(self.basedir)

    def tearDown(self):
        shutil.rmtree(self.basedir)

    def testStartStopRunningService(self):
        is_running = Dispatcher.service_running('postgresql')
        Dispatcher.start_service('postgresql')
        self.assertTrue(Dispatcher.service_running('postgresql'))
        Dispatcher.stop_service('postgresql')
        self.assertFalse(Dispatcher.service_running('postgresql'))
        if is_running:
            Dispatcher.start_service('postgresql')

    def testLoadServices(self):
        services_path = os.path.join(os.path.dirname(__file__), "../snap/backends/services/adapters")
        services = os.listdir(services_path)
        service_classes = []

        dispatcher = Dispatcher()

        for service in services:
            if service[0:8] != "__init__" and fnmatch.fnmatch(service, "*.py"):
                service = service.replace(".py", "")
                service_classes.append(dispatcher.load_service(service).__class__)

        # TODO for now just have services tested here statically set, perhaps a better way TODO this?
        self.assertIn(snap.backends.services.adapters.iptables.Iptables,     service_classes)
        self.assertIn(snap.backends.services.adapters.postgresql.Postgresql, service_classes)
        self.assertIn(snap.backends.services.adapters.mysql.Mysql,           service_classes)
        self.assertIn(snap.backends.services.adapters.mock.Mock,             service_classes)

    def testDispatcherBackup(self):
        dispatcher = snap.backends.services.dispatcher.Dispatcher()
        dispatcher.backup(self.basedir, include=['mock'])

        self.assertTrue(snap.backends.services.adapters.mock.Mock.backup_called)
        self.assertTrue(os.path.isfile(self.basedir + "/services.xml"))

        record = ServicesRecordFile(self.basedir + "/services.xml")
        services = record.read()
        service_names = []
        for service in services:
            service_names.append(service.name)
        self.assertIn("mock", service_names)

    def testDispatcherRestore(self):
        # first backup the mock service
        dispatcher = snap.backends.services.dispatcher.Dispatcher()
        dispatcher.backup(self.basedir, include=['mock'])

        # then restore it
        dispatcher.restore(self.basedir)
        self.assertTrue(snap.backends.services.adapters.mock.Mock.restore_called)

    def testSetAndRestorePythonUser(self):
        real_user = os.geteuid()
        real_dir  = os.getcwd()
        stored_user, stored_dir = snap.backends.services.adapters.postgresql.Postgresql.set_postgres_user()
        self.assertEqual(real_user, stored_user)
        self.assertEqual(real_dir, stored_dir)

        p_user = os.geteuid()
        p_dir  = os.getcwd()
        pg_user = pwd.getpwnam('postgres')
        self.assertEqual(p_user, pg_user.pw_uid)
        self.assertEqual(p_dir, pg_user.pw_dir)

        snap.backends.services.adapters.postgresql.Postgresql.restore_user(real_user, real_dir)
        self.assertEqual(real_user, os.geteuid())
        self.assertEqual(real_dir, os.getcwd())

    def testPostgresqlDbExists(self):
        is_running = Dispatcher.service_running('postgresql')
        Dispatcher.start_service('postgresql')
        self.assertTrue(snap.backends.services.adapters.postgresql.Postgresql.db_exists('postgres'))
        self.assertFalse(snap.backends.services.adapters.postgresql.Postgresql.db_exists('non-existant-db'))
        if not is_running:
            Dispatcher.stop_service('postgresql')

    def testPostgresqlCreateDropDb(self):
        is_running = Dispatcher.service_running('postgresql')
        Dispatcher.start_service('postgresql')
        snap.backends.services.adapters.postgresql.Postgresql.create_db('test_db')
        self.assertTrue(snap.backends.services.adapters.postgresql.Postgresql.db_exists('test_db'))
        snap.backends.services.adapters.postgresql.Postgresql.drop_db('test_db')
        self.assertFalse(snap.backends.services.adapters.postgresql.Postgresql.db_exists('test_db'))
        if not is_running:
            Dispatcher.stop_service('postgresql')

    def testPostgresqlService(self):
        # can't use basedir as the postgres user needs access to this
        pdir = '/tmp/snap-postgres'
        if not os.path.isdir(pdir):
            os.mkdir(pdir)
            os.chmod(pdir, 0777)

        # first start the service if it isn't running
        already_running=Dispatcher.service_running('postgresql')
        if not already_running:
            Dispatcher.start_service('postgresql')

        # create a test database
        snap.backends.services.adapters.postgresql.Postgresql.create_db('snaptest')

        # restore to original state
        if not already_running:
            Dispatcher.stop_service('postgresql')

        backend = snap.backends.services.adapters.postgresql.Postgresql()
        backend.backup(pdir)

        # ensure the process is in its original state
        currently_running=Dispatcher.service_running('postgresql')
        self.assertEqual(already_running, currently_running)

        # assert the db dump exists and has the db dump
        self.assertTrue(os.path.isfile(pdir + "/dump.psql"))
        f=file(pdir + "/dump.psql", 'r')
        c=f.read()
        f.close()
        self.assertEqual(1, len(re.findall('CREATE DATABASE snaptest', c)))

        # finally cleanup
        Dispatcher.start_service('postgresql')
        snap.backends.services.adapters.postgresql.Postgresql.drop_db('snaptest')

        # stop the service, backup the datadir
        Dispatcher.stop_service('postgresql')
        shutil.copytree(snap.backends.services.adapters.postgresql.Postgresql.DATADIR, 
                        snap.backends.services.adapters.postgresql.Postgresql.DATADIR + ".bak")

        # test restore
        backend.restore(pdir)

        # ensure service is running, datadir has been initialized
        self.assertTrue(Dispatcher.service_running('postgresql'))
        self.assertTrue(os.path.isdir(snap.backends.services.adapters.postgresql.Postgresql.DATADIR))

        # ensure the db exists
        self.assertTrue(snap.backends.services.adapters.postgresql.Postgresql.db_exists('snaptest'))

        # stop the service, restore the db
        Dispatcher.stop_service('postgresql')
        shutil.rmtree(snap.backends.services.adapters.postgresql.Postgresql.DATADIR)
        shutil.move(snap.backends.services.adapters.postgresql.Postgresql.DATADIR + ".bak",
                    snap.backends.services.adapters.postgresql.Postgresql.DATADIR)
        # XXX dirty hack make sure the datadir is owned by postgres
        if snap.backends.services.adapters.postgresql.Postgresql.current_os == 'ubuntu' or \
           snap.backends.services.adapters.postgresql.Postgresql.current_os == 'debian':
            data_dir=snap.backends.services.adapters.postgresql.Postgresql.DATADIR + "/../../"
            pg_user = pwd.getpwnam('postgres')
            for root, dirs, files in os.walk(data_dir):
                for d in dirs:
                    os.chown(os.path.join(root, d), pg_user.pw_uid, pg_user.pw_gid) 
                for f in files:
                    os.chown(os.path.join(root, f), pg_user.pw_uid, pg_user.pw_gid) 

        # cleanup, restore to original state
        if already_running:
            Dispatcher.start_service('postgresql')

        shutil.rmtree(pdir)

    def testMysqlDbExists(self):
        is_running = Dispatcher.service_running(snap.backends.services.adapters.mysql.Mysql.DAEMON)
        Dispatcher.start_service(snap.backends.services.adapters.mysql.Mysql.DAEMON)
        self.assertTrue(snap.backends.services.adapters.mysql.Mysql.db_exists('mysql'))
        self.assertFalse(snap.backends.services.adapters.mysql.Mysql.db_exists('non-existant-db'))
        if not is_running:
            Dispatcher.stop_service(snap.backends.services.adapters.mysql.Mysql.DAEMON)

    def testMysqlCreateDropDb(self):
        is_running = Dispatcher.service_running(snap.backends.services.adapters.mysql.Mysql.DAEMON)
        Dispatcher.start_service(snap.backends.services.adapters.mysql.Mysql.DAEMON)
        snap.backends.services.adapters.mysql.Mysql.create_db('snap_test_db')
        self.assertTrue(snap.backends.services.adapters.mysql.Mysql.db_exists('snap_test_db'))
        snap.backends.services.adapters.mysql.Mysql.drop_db('snap_test_db')
        self.assertFalse(snap.backends.services.adapters.mysql.Mysql.db_exists('snap_test_db'))
        if not is_running:
            Dispatcher.stop_service(snap.backends.services.adapters.mysql.Mysql.DAEMON)

    def testMysqlService(self):
        mdir = '/tmp/snap-mysql'
        if not os.path.isdir(mdir):
            os.mkdir(mdir)

        # first start the service if it isn't running
        already_running=Dispatcher.service_running(snap.backends.services.adapters.mysql.Mysql.DAEMON)
        if not already_running:
            Dispatcher.start_service(snap.backends.services.adapters.mysql.Mysql.DAEMON)

        # create a test database
        snap.backends.services.adapters.mysql.Mysql.create_db('snaptest')

        # restore to original state
        if not already_running:
            Dispatcher.stop_service(snap.backends.services.adapters.mysql.Mysql.DAEMON)

        backend = snap.backends.services.adapters.mysql.Mysql()
        backend.backup(mdir)

        # ensure the process is in its original state
        currently_running=Dispatcher.service_running(snap.backends.services.adapters.mysql.Mysql.DAEMON)
        self.assertEqual(already_running, currently_running)

        # assert the db dump exists and has the db dump
        self.assertTrue(os.path.isfile(mdir + "/dump.mysql"))
        f=file(mdir + "/dump.mysql", 'r')
        c=f.read()
        f.close()
        self.assertEqual(1, len(re.findall('CREATE DATABASE.*snaptest', c)))

        # finally cleanup
        Dispatcher.start_service(snap.backends.services.adapters.mysql.Mysql.DAEMON)
        snap.backends.services.adapters.mysql.Mysql.drop_db('snaptest')

        # stop the service, backup the datadir
        Dispatcher.stop_service(snap.backends.services.adapters.mysql.Mysql.DAEMON)
        shutil.copytree(snap.backends.services.adapters.mysql.Mysql.DATADIR,
                        snap.backends.services.adapters.mysql.Mysql.DATADIR + ".bak")

        # test restore
        backend.restore(mdir)

        # ensure service is running, datadir has been initialized
        self.assertTrue(Dispatcher.service_running(snap.backends.services.adapters.mysql.Mysql.DAEMON))
        self.assertTrue(os.path.isdir(snap.backends.services.adapters.mysql.Mysql.DATADIR))

        # ensure the db exists
        self.assertTrue(snap.backends.services.adapters.mysql.Mysql.db_exists('snaptest'))

        # stop the service, restore the db
        Dispatcher.stop_service(snap.backends.services.adapters.mysql.Mysql.DAEMON)
        shutil.rmtree(snap.backends.services.adapters.mysql.Mysql.DATADIR)
        shutil.move(snap.backends.services.adapters.mysql.Mysql.DATADIR + ".bak",
                    snap.backends.services.adapters.mysql.Mysql.DATADIR)
        # XXX dirty hack make sure the datadir is owned by postgres
        if snap.backends.services.adapters.mysql.Mysql.current_os == 'ubuntu' or \
           snap.backends.services.adapters.mysql.Mysql.current_os == 'debian':
            data_dir=snap.backends.services.adapters.mysql.Mysql.DATADIR
            my_user = pwd.getpwnam('mysql')
            for root, dirs, files in os.walk(data_dir):
                os.chown(root, my_user.pw_uid, my_user.pw_gid) 
                for d in dirs:
                    os.chown(os.path.join(root, d), my_user.pw_uid, my_user.pw_gid) 
                for f in files:
                    os.chown(os.path.join(root, f), my_user.pw_uid, my_user.pw_gid) 

        # cleanup, restore to original state
        if already_running:
            Dispatcher.start_service(snap.backends.services.adapters.mysql.Mysql.DAEMON)

        shutil.rmtree(mdir)

    def testIptablesService(self):
        # manually backup iptalbes to restore after the test
        f=file(self.basedir + "/iptables-backup", 'w')
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
        f = open(self.basedir + "/iptables.rules", 'r')
        c = f.read()
        f.close
        self.assertEqual(1, len(re.findall('-A INPUT -p tcp -m tcp --dport 22 -j ACCEP', c)))

        # again flush the filter table
        popen = subprocess.Popen(["iptables", "-F"])
        popen.wait()
        self.assertEqual(0, popen.returncode)

        # perform the restoration
        backend.restore(self.basedir)

        # assert that we have registered port 22
        f=file(self.basedir + "/iptables-running", 'w')
        popen = subprocess.Popen(["iptables", "-nvL"], stdout=f)
        popen.wait()
        self.assertEqual(0, popen.returncode)
        f=file(self.basedir + "/iptables-running", 'r')
        c = f.read()
        c = re.sub("\s+", " ", c)
        f.close()
        self.assertEqual(1, 
          len(re.findall("ACCEPT.*tcp dpt:22", c))) # TODO prolly could be a better regex
          

        # finally fiush the chain one last time and restore the original rules
        popen = subprocess.Popen(["iptables", "-F"])
        popen.wait()
        self.assertEqual(0, popen.returncode)
        popen = subprocess.Popen(["iptables-restore", self.basedir + "/iptables-backup"])
        popen.wait()
        self.assertEqual(0, popen.returncode)
