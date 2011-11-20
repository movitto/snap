#!/usr/bin/python
#
# Postgresql service backup/restoration adapter
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
import tempfile
import subprocess

import snap
from snap.osregistry import OS, OSUtils
from snap.backends.services.dispatcher import Dispatcher

class Postgresql:

    if OS.yum_based():
        DATADIR = '/var/lib/pgsql/data'
        DAEMON = 'postgresql'
        PSQL_CMD = '/usr/bin/psql'
        PGDUMPALL_CMD = '/usr/bin/pg_dumpall'

        # hack until we re-introduce package system abstraction:
        PREREQ_INSTALL_COMMAND = 'yum install -y postgresql-server postgresql'

    elif OS.apt_based() and os.path.isdir('/var/lib/postgresql'):
        VERSION = os.listdir('/var/lib/postgresql')[0]
        DATADIR = '/var/lib/postgresql/' + VERSION + '/main'
        DAEMON = 'postgresql'
        PSQL_CMD = '/usr/bin/psql'
        PGDUMPALL_CMD = '/usr/bin/pg_dumpall'

        # hack until we re-introduce package system abstraction:
        PREREQ_INSTALL_COMMAND = 'apt-get install -y postgresql'
        
    elif OS.is_windows() and os.path.isdir("C:\Program Files\PostgreSQL"):
        VERSION = os.listdir('C:\Program Files\PostgreSQL')[0]
        DATADIR = os.path.join("C:\Program Files\PostgreSQL", VERSION, "data")
        DAEMON = 'postgresql-x64-' + VERSION # FIXME also support 32 bit
        PSQL_CMD = os.path.join("C:\Program Files\PostgreSQL", VERSION, "bin\psql.exe")
        PGDUMPALL_CMD = os.path.join("C:\Program Files\PostgreSQL", VERSION, "bin\pg_dumpall.exe")
    
    else:
        VERSION = None
        DATADIR = None
        DAEMON = None
        PSQL_CMD = None
        PGDUMPALL_CMD = None
    
    def set_pgpassword_env():
        '''helper to set the postgres password in the env from the config'''
        pgpassword = snap.config.options.service_options['postgresql_password']
        penv = os.environ
        penv['PGPASSWORD'] = pgpassword
        return penv
    set_pgpassword_env = staticmethod(set_pgpassword_env)

    def db_exists(dbname):
        '''helper to return boolean indicating if the db w/ the specified name exists'''
        null = open(OSUtils.null_file(), 'w')

        # get the env containing the postgres password
        penv = Postgresql.set_pgpassword_env()

        # retrieve list of db names from postgres
        t = tempfile.TemporaryFile()
        popen = subprocess.Popen([Postgresql.PSQL_CMD, "--username", "postgres", "-t", "-c", "select datname from pg_database"],
                                 env=penv, stdout=t, stderr=null)
        popen.wait()

        # determine if the specified one is among them
        t.seek(0)
        c = t.read()
        has_db = len(re.findall(dbname, c))

        return has_db
    db_exists = staticmethod(db_exists)
    
    def create_db(dbname):
        '''helper to create the specified database'''
        null = open(OSUtils.null_file(), 'w')
        
        # get env containing the postgres password
        penv = Postgresql.set_pgpassword_env()

        # create the db
        popen = subprocess.Popen([Postgresql.PSQL_CMD, "--username", "postgres", "-c", "CREATE DATABASE " + dbname],
                                 env=penv, stdout=null, stderr=null)
        popen.wait()
    create_db = staticmethod(create_db)

    def drop_db(dbname):
        '''helper to drop the specified database'''
        null = open(OSUtils.null_file(), 'w')

        # get env containing the postgres password
        penv = Postgresql.set_pgpassword_env()

        # destroy the db
        popen = subprocess.Popen([Postgresql.PSQL_CMD, "--username", "postgres", "-c", "DROP DATABASE " + dbname],
                                 env=penv, stdout=null, stderr=null)
        popen.wait()
    drop_db = staticmethod(drop_db)

    def set_root_pass():
        '''helper to clear the postgresql root password'''
        # !!!FIXME!!! implement, can be accomplished by su'ing to the postgres user on linux
    set_root_pass = staticmethod(set_root_pass)

    def init_db():
        '''helper to initialize the database server'''

        # db already initialized, just return
        if os.path.isdir(Postgresql.DATADIR) and len(os.listdir(Postgresql.DATADIR)) > 0:
            return

        null = open(OSUtils.null_file(), 'w')

        # FIXME should run initdb manually
        popen = subprocess.Popen(["service", "postgresql", "initdb"], stdout=null)
        popen.wait()
    init_db = staticmethod(init_db)

    def is_available(self):
        '''return true postgres is available locally'''
        return os.path.isdir(Postgresql.DATADIR)

    def install_prereqs(self):
        if OS.is_linux():
            popen = subprocess.Popen(Postgresql.PREREQ_INSTALL_COMMAND.split())
            popen.wait()
        # !!!FIXME!!! it is possible to install postgresql in an automated / 
        # non-interactive method on windows, implement this!!!

    def backup(self, basedir):
        dispatcher = Dispatcher.os_dispatcher()
        null = open(OSUtils.null_file(), 'w')
                
        if OS.is_linux():
            Postgresql.set_root_pass()
        
        # check to see if service is running
        already_running = dispatcher.service_running(Postgresql.DAEMON)

        # start the postgresql server
        dispatcher.start_service(Postgresql.DAEMON)

        # get env containing postgres password
        penv = Postgresql.set_pgpassword_env()

        outfile = file(basedir + "/dump.psql", "w")
        pipe = subprocess.Popen([Postgresql.PGDUMPALL_CMD, "--username", "postgres"],
                                env=penv, stdout=outfile, stderr=null)
        pipe.wait()

        # if postgresql was running b4hand, start up again
        if not already_running:
            dispatcher.stop_service(Postgresql.DAEMON)

    def restore(self, basedir):
        dispatcher = Dispatcher.os_dispatcher()
        null = open(OSUtils.null_file(), 'w')
        
        if OS.is_linux():
            Postgresql.set_root_pass()

        # init the postgresql db
        Postgresql.init_db()

        # start the postgresql service
        dispatcher.start_service(Postgresql.DAEMON)

        # get env containing the postgresql password
        penv = Postgresql.set_pgpassword_env()

        # use pipe to invoke postgres, restoring database
        infile = file(basedir + "/dump.psql", "r")
        popen = subprocess.Popen([Postgresql.PSQL_CMD, "--username", "postgres"],
                                 env=penv, stdin=infile, stdout=null, stderr=null)
        popen.wait()
