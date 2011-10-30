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

from snap.backends.services.dispatcher import Dispatcher

class Mysql:

    def db_exists(dbname):
        '''helper to return boolean indicating if the db w/ the specified name exists'''
        null=open('/dev/null', 'w')

        # retrieve list of db names from postgres
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

    def backup(self, basedir):
        null=open('/dev/null', 'w')

        # check to see if service is running
        already_running = Dispatcher.service_running('mysqld') 

        # start the mysql server
        Dispatcher.start_service('mysqld')

        # use a pipe to invoke mysqldump and capture output
        outfile = file(basedir + "/dump.mysql", "w")
        popen = subprocess.Popen(["mysqldump", "--all-databases"], stdout=outfile, stderr=null)
        popen.wait()

        # if mysql was stopped b4hand, start up again
        if not already_running:
            Dispatcher.stop_service('mysqld')

    def restore(self, basedir):
        null=open('/dev/null', 'w')

        # start the mysql server
        popen = subprocess.Popen(["service", "mysqld", "start"], stdout=null, stderr=null)
        popen.wait()

        # use pipe to invoke mysql, restoring database
        infile = file(basedir + "/dump.mysql", "r")
        popen = subprocess.Popen("mysql", stdin=infile, stdout=null, stderr=null)
        popen.wait()
