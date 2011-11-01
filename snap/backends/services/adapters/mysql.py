#!/usr/bin/python
#
# Mysql service backup/restoration adapter
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

# TODO at some point use the mysql-python api to
# implement something akin to pg_dump / pg_dumpall

import os
import re
import tempfile
import subprocess

import snap
from snap.backends.services.dispatcher import Dispatcher

class Mysql:

    if snap.osregistry.OS.yum_based():
        DAEMON='mysqld'

        # hack until we re-introduce package system abstraction:
        PREREQ_INSTALL_COMMAND='yum install mysql-server mysql'

    elif snap.osregistru.OS.apt_based():
        DAEMON='mysql'

        # hack until we re-introduce package system abstraction:
        PREREQ_INSTALL_COMMAND='apt-get install mysql-server mysql-client'

    DATADIR='/var/lib/mysql'

    def db_exists(dbname):
        '''helper to return boolean indicating if the db w/ the specified name exists'''
        null=open('/dev/null', 'w')

        # retrieve list of db names from mysql
        t = tempfile.TemporaryFile()
        popen = subprocess.Popen(["mysql", "-e", "show databases"], stdout=t, stderr=null)
        popen.wait()

        # determine if the specified one is among them
        t.seek(0)
        c = t.read()
        has_db = len(re.findall(dbname, c))

        return has_db
    db_exists=staticmethod(db_exists)

    def create_db(dbname):
        '''helper to create the specified database'''
        null=open('/dev/null', 'w')

        # create the db
        popen = subprocess.Popen(["mysqladmin", "create", dbname], stdout=null, stderr=null)
        popen.wait()
    create_db=staticmethod(create_db)

    def drop_db(dbname):
        '''helper to drop the specified database'''
        null=open('/dev/null', 'w')

        # destroy the db
        popen = subprocess.Popen(["mysqladmin", "-f", "drop", dbname], stdout=null, stderr=null)
        popen.wait()
    drop_db=staticmethod(drop_db)

    def clear_root_pass():
        '''helper to clear the mysql root password'''
        # TODO at somepoint retrieve / return the root password to restore later

        already_running = Dispatcher.service_running(Mysql.DAEMON)
        if already_running:
            Dispatcher.stop_service(Mysql.DAEMON)

        server = subprocess.Popen(['mysqld_safe', '--skip-grant-tables'])
        client = subprocess.Popen(['mysql', 'mysql', '-u', 'root', '-e', 'update user set password=PASSWORD("") where user="root"; flush privileges;'])
        client.kill()
        server.kill()

        if already_running:
            Dispatcher.start_service(Mysql.DAEMON)
    clear_root_pass=staticmethod(clear_root_pass)

    def is_available(self):
        '''return true if we're on a linux system and the init script is available'''
        return snap.osregistry.OS.is_linux() and os.path.isfile("/etc/init.d/" + Mysql.DAEMON)

    def is_available(self):
        '''return true if we're on a linux system and the init script is available'''
        return snap.osregistry.OS.is_linux() and os.path.isfile("/etc/init.d/" + Mysql.DAEMON)

    def install_prereqs(self):
        popen = subprocess.Popen(PREREQ_INSTALL_COMMAND.split())
        popen.wait()

    def backup(self, basedir):
        null=open('/dev/null', 'w')

        if snap.osregistry.OS.apt_based():
            Mysql.clear_root_pass()

        # check to see if service is running
        already_running = Dispatcher.service_running(Mysql.DAEMON) 

        # start the mysql server
        Dispatcher.start_service(Mysql.DAEMON)

        # use a pipe to invoke mysqldump and capture output
        outfile = file(basedir + "/dump.mysql", "w")
        popen = subprocess.Popen(["mysqldump", "--all-databases"], stdout=outfile, stderr=null)
        popen.wait()

        # if mysql was stopped b4hand, start up again
        if not already_running:
            Dispatcher.stop_service(Mysql.DAEMON)

    def restore(self, basedir):
        null=open('/dev/null', 'w')

        if snap.osregistry.OS.apt_based():
            Mysql.clear_root_pass()

        # start the mysql server
        Dispatcher.start_service(Mysql.DAEMON)

        # use pipe to invoke mysql, restoring database
        infile = file(basedir + "/dump.mysql", "r")
        popen = subprocess.Popen("mysql", stdin=infile, stdout=null, stderr=null)
        popen.wait()
