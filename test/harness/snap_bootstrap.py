#!/usr/bin/python
#
# test program the runs on the vm to install snap and run operations
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
import sys
import subprocess
import tempfile

SNAP_SOURCE_GIT = 'git://github.com/movitto/snap.git'

# grab type of vm we are installing on via cmd line argument
UNDERLYING_OS = sys.argv[1]

# grab mode of operation from second command line argument
SNAP_MODE = sys.argv[2]

# source location of snap binaries
SNAP_INSTALL_LOCATION=None
if UNDERLYING_OS == 'fedora':
    SNAP_INSTALL_LOCATION='http://yum.morsi.org/repos/15/'
elif UNDERLYING_OS == 'ubuntu':
    SNAP_INSTALL_LOCATION='http://apt.morsi.org/ubuntu/'
#elif UNDERLYING_OS == 'windows_xp':
#elif UNDERLYING_OS == 'windows_7':

# helper to run a command and wait for it to complete, returns the command's stdout/stderr
def run_command(command):
    t = tempfile.TemporaryFile()
    popen = subprocess.Popen(command, stdout=t, stderr=t)
    popen.wait()
    t.seek(0)
    data = t.read()
    t.close()
    return data


# helper to install test suite prerequisites
def setup_tests():
    if UNDERLYING_OS == 'fedora':
        # install git and test suite prereqs
        run_command(['yum', 'install', '--nogpgcheck', "-y", "git", "postgresql-server", "postgresql", "httpd", "mysql-server", "mysql" ])
    
        # setup postgres as a test suite prereq
        run_command(['service', 'postgresql', 'initdb'])

    elif UNDERLYING_OS == 'fedora':
        run_command(['apt-get', 'install', "-y", "git", "postgresql", "apache2", "mysql-server", "mysql-client"])

    # setup postgres root password
    #run_command(['su', 'postgres', '-c', '"psql', '-c', '\"alter', 'user', 'postgres', 'with', 'password', "'postgres'" '\""'])

    # XXX hack allow anyone to connect to postgres
    run_command(["sed", "-i", "s/ident/trust/", "/var/lib/pgsql/data/pg_hba.conf"])

    # restart postgres
    run_command(["service", "postgresql", "start"])

    # start mysql
    run_command(["service", "mysqld", "start"])

    # setup mysql root password
    run_command(["mysqladmin", "-u", "root", "password", "mysql"])

# helper to run tests
def run_tests():
    # clone source (to run tests)
    run_command(["git", "clone", SNAP_SOURCE_GIT])
    
    # run the tests
    os.chdir("snap")
    output = run_command(["make", "test"])
    failed = re.search('FAIL', output) != None or re.search('ERROR', output) != None
    if failed:
       print "ERROR: running snap tests"
       print output
       return
    os.chdir("..")

# helper to create mock data
def create_mock_data():
    if UNDERLYING_OS == 'fedora':
        run_command(['yum', 'install', "-y", "mediawiki", "postgresql-server"])
    elif UNDERLYING_OS == 'ubuntu':
        run_command(['apt-get', 'install', "-y", "mediawiki", "postgresql"])

    run_command(['iptables', '-A', 'INPUT', '-p', 'tcp', '--dport', '1234', '-j', 'ACCEPT'])
    run_command(['service', 'postgresql', 'initdb'])
    # XXX hack
    run_command(["sed", "-i", "s/ident/trust/", "/var/lib/pgsql/data/pg_hba.conf"])
    run_command(['service', 'postgresql', 'start'])
    run_command(['psql', 'postgres', 'postgres', '-c', 'create database snap_test'])
    run_command(['psql', 'snap_test', 'postgres', '-c', 'create table snap_table (id int, name varchar(50))'])
    run_command(['psql', 'snap_test', 'postgres', '-c', "insert into snap_table values (1, 'mo')"])
    o = open("/etc/dummy.conf", "w")
    o.write("dummy.conf")
    o.close()
    o = open("/var/dummy.data", "w")
    o.write("dummy.data")
    o.close()

# helper to verify mock data is restored
def verify_mock_data():
    # instead of assertions, we simply output any errors so that the invoker
    # script can detect this
    output = None
    result = None
    if UNDERLYING_OS == 'fedora':
      output = run_command(['rpm', '-q', 'mediawiki', 'postgresql-server'])
      result = re.search('not installed', output)
    elif UNDERLYING_OS == 'ubuntu':
      output = run_command(['rpm', '-q', 'mediawiki', 'postgresql-server'])
      result = re.search('No packages found', output)
    if result != None:
        print "ERROR: mediawiki and postgresql-server not found"

    output = run_command(['iptables', '-nvL'])
    result = re.search('ACCEPT.*tcp dpt:1234', output)
    if result == None:
        print "ERROR: iptables not properly restored"

    output = run_command(['psql', 'snap_test', 'postgres', '-t', '-c', 'select * from snap_table'])
    result = re.search('1 | mo', output)
    if result == None:
        print "ERROR: postgresql not restored"

    o = open("/etc/dummy.conf", 'r')
    output = o.read()
    o.close()
    result = re.search('dummy.conf', output)
    if result == None:
        print "ERROR: dummy.conf file not restored"

# helper to install snap
def install_snap():
    if UNDERLYING_OS == 'fedora':
        # setup repo
        o = open("/etc/yum.repos.d/snap.repo", "w")
        o.write("[snap]\nname=snap yum repository\nbaseurl="+SNAP_INSTALL_LOCATION+"\nenabled=1\nskip_if_unavailable=1\ngpgcheck=0")
        o.close()
    
        # install snap
        run_command(['yum', 'install', '--nogpgcheck', "-y", "snap"])
    
    elif UNDERLYING_OS == 'ubuntu':
    
        # setup repo
        o = open("/etc/apt/sources.list", "a")
        o.write("deb " + SNAP_INSTALL_LOCATION + " oneiric main\ndeb-src " + SNAP_INSTALL_LOCATION + "oneiric main")
        o.close()
    
        # install snap
        run_command(['apt-get', 'install', "-y", "snap"])
    
    #elif UNDERLYING_OS == 'windows_xp':
    
    #elif UNDERLYING_OS == 'windows_7':

# disable selinux
run_command(['setenforce', '0'])

if SNAP_MODE == 'backup':
    # setup mock data
    create_mock_data()

    # install snap
    install_snap()

    # run the actual backup
    run_command(['/usr/bin/snaptool', '--backup', '--snapfile', '/tmp/snapfile.tgz', '--repos', '--packages', '--files', '--services'])

elif SNAP_MODE == 'restore':
    # install snap
    install_snap()

    # XXX hack to remove postgres permissions
    run_command(["yum", "install", "-y", "postgresql-server"])
    run_command(["service", "postgresql", "initdb"])
    run_command(["sed", "-i", "s/ident/trust/", "/var/lib/pgsql/data/pg_hba.conf"])

    # run the actual restoration
    run_command(['/usr/bin/snaptool', '--restore', '--snapfile', '/tmp/snapfile.tgz'])

    # verify mock data is restored
    verify_mock_data()

elif SNAP_MODE == 'test':
    # setup test prerequisites
    setup_tests()

    # checkout the source / run the test suite
    run_tests()
