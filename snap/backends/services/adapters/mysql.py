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

import os
import re
import subprocess

import snap
from snap.osregistry import OS, OSUtils
from snap.backends.services.dispatcher import Dispatcher
from snap.filemanager import FileManager

class Mysql:

    if snap.osregistry.OS.yum_based():
        DAEMON = 'mysqld'
        DATADIR = '/var/lib/mysql'
        MYSQL_CMD = '/usr/bin/mysql'
        MYSQLADMIN_CMD = "/usr/bin/mysqladmin"
        MYSQLDSAFE_CMD = "/usr/bin/mysqld_safe"
        MYSQLDUMP_CMD = "/usr/bin/mysqldump"

        # hack until we re-introduce package system abstraction:
        PREREQ_INSTALL_COMMAND = 'yum install -y mysql-server mysql'

    elif snap.osregistry.OS.apt_based():
        DAEMON = 'mysql'
        DATADIR = '/var/lib/mysql'
        MYSQL_CMD = '/usr/bin/mysql'
        MYSQLADMIN_CMD = "/usr/bin/mysqladmin"
        MYSQLDSAFE_CMD = "/usr/bin/mysqld_safe"
        MYSQLDUMP_CMD = "/usr/bin/mysqldump"

        # hack until we re-introduce package system abstraction:
        PREREQ_INSTALL_COMMAND = 'apt-get install -y mysql-server mysql-client'

    elif snap.osregistry.OS.is_windows() and os.path.isdir('C:\\Program Files\\MySQL'):
        VERSION = os.listdir('C:\\Program Files\\MySQL')[0].replace("MySQL Server ", "")
        DATADIR = "C:\\Program Files\\MySQL\\MySQL Server " + VERSION + "\\data"
        MYSQL_CMD = "C:\\Program Files\\MySQL\\MySQL Server " + VERSION + "\\bin\mysql.exe"
        MYSQLADMIN_CMD = "C:\\Program Files\\MySQL\\MySQL Server " + VERSION + "\\bin\\mysqladmin.exe"
        MYSQLDSAFE_CMD = "C:\\Program Files\\MySQL\\MySQL Server " + VERSION + "\\bin\\mysqld_safe.exe"
        MYSQLDUMP_CMD = "C:\\Program Files\\MySQL\\MySQL Server " + VERSION + "\\bin\\mysqldump.exe"
        DAEMON = 'MySQL'

    else:
        VERSION = None
        DATADIR = None
        DAEMON = None
        MYSQL_CMD = None
        MYSQLADMIN_CMD = None
        MYSQLDSAFE_CMD = None

    def db_exists(dbname):
        '''helper to return boolean indicating if the db w/ the specified name exists'''
        mysql_password = snap.config.options.service_options['mysql_password']

        # retrieve list of db names from mysql
        c = FileManager.capture_output([Mysql.MYSQL_CMD, "-e", "show databases", "-u", "root", "-p" + mysql_password])

        # determine if the specified one is among them
        has_db = len(re.findall(dbname, c))

        return has_db
    db_exists = staticmethod(db_exists)

    def flush_privileges():
        '''helper to flush database privileges'''
        null = open(OSUtils.null_file(), 'w')
        
        mysql_password = snap.config.options.service_options['mysql_password']

        popen = subprocess.Popen([Mysql.MYSQL_CMD, "-p" + mysql_password, "-e", "flush privileges;"],
                                 stdout=null, stderr=null)
        popen.wait()
    flush_privileges = staticmethod(flush_privileges)

    def create_db(dbname):
        '''helper to create the specified database'''
        null = open(OSUtils.null_file(), 'w')
        
        mysql_password = snap.config.options.service_options['mysql_password']

        # create the db
        popen = subprocess.Popen([Mysql.MYSQLADMIN_CMD, "-u", "root", "-p" + mysql_password, "create", dbname],
                                 stdout=null, stderr=null)
        popen.wait()
    create_db = staticmethod(create_db)

    def drop_db(dbname):
        '''helper to drop the specified database'''
        null = open(OSUtils.null_file(), 'w')

        mysql_password = snap.config.options.service_options['mysql_password']

        # destroy the db
        popen = subprocess.Popen([Mysql.MYSQLADMIN_CMD, "-u", "root", "-p" + mysql_password, "-f", "drop", dbname],
                                 stdout=null, stderr=null)
        popen.wait()
    drop_db = staticmethod(drop_db)

    def set_root_pass():
        '''helper to set the mysql root password'''
        null = open(OSUtils.null_file(), 'w')
        dispatcher = Dispatcher.os_dispatcher()
        
        mysql_password = snap.config.options.service_options['mysql_password']
        
        already_running = dispatcher.service_running(Mysql.DAEMON)
        if already_running:
            dispatcher.stop_service(Mysql.DAEMON)

        server = subprocess.Popen([Mysql.MYSQLDSAFE_CMD, '--skip-grant-tables'], stdout=null, stderr=null)
        client = subprocess.Popen([Mysql.MYSQL_CMD, 'mysql', '-u', 'root', '-e', "update user set password=PASSWORD('" + mysql_password + "') where user='root'; flush privileges;"],
                                  stdout=null, stderr=null)
        client.wait()
        client = subprocess.Popen([Mysql.MYSQLADMIN_CMD, 'shutdown'], stdout=null, stderr=null)
        client.wait()
        if server.poll() == None: # race condition?
            server.kill()

        if already_running:
            dispatcher.start_service(Mysql.DAEMON)
    set_root_pass = staticmethod(set_root_pass)

    def is_available(self):
        '''return true if we're on a linux system and the init script is available'''
        return Mysql.DATADIR and os.path.isdir(Mysql.DATADIR)

    def install_prereqs(self):
        if OS.is_linux():
            env=os.environ
            env['DEBIAN_FRONTEND']='noninteractive'
            popen = subprocess.Popen(Mysql.PREREQ_INSTALL_COMMAND.split(), env=env)
            popen.wait()
        # !!!FIXME!!! it is possible to install mysql in an automated / 
        # non-interactive method on windows, implement this!!!

    def backup(self, basedir):
        dispatcher = Dispatcher.os_dispatcher()
        null = open(OSUtils.null_file(), 'w')

        if OS.is_linux():
            Mysql.set_root_pass()

        mysql_password = snap.config.options.service_options['mysql_password']

        # check to see if service is running
        already_running = dispatcher.service_running(Mysql.DAEMON) 

        # start the mysql server
        dispatcher.start_service(Mysql.DAEMON)

        # use a pipe to invoke mysqldump and capture output
        outfile = file(basedir + "/dump.mysql", "w")
        popen = subprocess.Popen([Mysql.MYSQLDUMP_CMD, "-u", "root", "-p" + mysql_password, "--all-databases"],
                                 stdout=outfile, stderr=null)
        popen.wait()

        # if mysql was stopped b4hand, start up again
        if not already_running:
            dispatcher.stop_service(Mysql.DAEMON)

    def restore(self, basedir):
        dispatcher = Dispatcher.os_dispatcher()
        null = open(OSUtils.null_file(), 'w')

        if OS.is_linux():
            Mysql.set_root_pass()

        mysql_password = snap.config.options.service_options['mysql_password']
        
        # start the mysql server
        dispatcher.start_service(Mysql.DAEMON)

        # use pipe to invoke mysql, restoring database
        infile = file(basedir + "/dump.mysql", "r")
        popen = subprocess.Popen([Mysql.MYSQL_CMD, "-u", "root", "-p" + mysql_password],
                                 stdin=infile, stdout=null, stderr=null)
        popen.wait()

        # flush privileges incase any roles were restored and whatnot
        Mysql.flush_privileges()
