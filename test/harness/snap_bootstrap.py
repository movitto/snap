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

# helper to run a command and wait for it to complete, returns the command's stdout/stderr
def run_command(command, env=os.environ, shell=False):
    t = tempfile.TemporaryFile()
    popen = subprocess.Popen(command, stdout=t, stderr=t, env=env, shell=shell)
    popen.wait()
    t.seek(0)
    data = t.read()
    t.close()
    return data

# XXX a hack we need to implement to get postgres working, remove this at some point
def postgres_hack():
    if UNDERLYING_OS == 'fedora':
        run_command(["yum", "install", "-y", "postgresql-server"])
        run_command(["service", "postgresql", "initdb"])
        run_command(["sed", "-i", "s/ident/trust/", "/var/lib/pgsql/data/pg_hba.conf"])
        run_command(['service', 'postgresql', 'start'])
    elif UNDERLYING_OS == 'ubuntu':
        run_command(["apt-get", "install", "-y", "postgresql"])
        run_command(["sed", "-i", "s/md5/trust/", "/etc/postgresql/9.1/main/pg_hba.conf"])
        run_command(["sed", "-i", "s/peer/trust/", "/etc/postgresql/9.1/main/pg_hba.conf"])
        run_command(['service', 'postgresql', 'restart'])


# helper to install test suite prerequisites
def setup_tests():
    if UNDERLYING_OS == 'fedora':
        # install git and test suite prereqs
        run_command(['yum', 'install', '--nogpgcheck', "-y", "git", "postgresql-server", "postgresql", "httpd", "mysql-server", "mysql" ])
    
        # XXX hack allow anyone to connect to postgres
        postgres_hack()

        # start mysql
        run_command(["service", "mysqld", "start"])

    elif UNDERLYING_OS == 'ubuntu':
        env = os.environ
        env['DEBIAN_FRONTEND']='noninteractive'
        run_command(['apt-get', 'install', "-y", "git", "postgresql", "apache2", "mysql-server", "mysql-client"], env=env)

        # XXX hack allow anyone to connect to postgres
        postgres_hack()

        # start mysql
        run_command(["service", "mysql", "start"])

    # setup postgres root password
    #run_command(['su', 'postgres', '-c', '"psql', '-c', '\"alter', 'user', 'postgres', 'with', 'password', "'postgres'" '\""'])

    # setup mysql root password
    run_command(["mysqladmin", "-u", "root", "password", "mysql"])

# helper build the package
def build_package():
    # install git
    if UNDERLYING_OS == 'fedora':
        run_command(['yum', 'install', '--nogpgcheck', "-y", "git", 'rpm-build', 'python2-devel'])

        if not os.path.isdir(os.path.expanduser("~") + "/rpmbuild/SOURCES"):
            os.mkdir(os.path.expanduser("~") + "/rpmbuild")
            os.mkdir(os.path.expanduser("~") + "/rpmbuild/SOURCES")

        if not os.path.isdir("snap"):
            # clone source
            run_command(["git", "clone", SNAP_SOURCE_GIT])

        os.chdir("snap")
        run_command(['make', 'rpm'])
        os.chdir("..")

    elif UNDERLYING_OS == 'ubuntu':
        run_command(['apt-get', 'install', "-y", "git", 'build-essential', 'devscripts', 'debhelper', 'cdbs'])

        if not os.path.isdir("snap"):
            # clone source
            run_command(["git", "clone", SNAP_SOURCE_GIT])

        os.chdir("snap")
        run_command(['make', 'deb'])
        os.chdir("..")


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
        env = os.environ
        env['DEBIAN_FRONTEND']='noninteractive'
        run_command(['apt-get', 'install', "-y", "mediawiki", "postgresql"], env=env)

    run_command(['iptables', '-A', 'INPUT', '-p', 'tcp', '--dport', '1234', '-j', 'ACCEPT'])
    postgres_hack()
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
      output = run_command(['dpkg-query', '-s', 'mediawiki', 'postgresql'])
      result = re.search('not installed', output)
    if result != None:
        print "ERROR: mediawiki and postgresql not found"

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
        # install snap
        run_command('yum install --nogpgcheck -y *.rpm', shell=True)
    
    elif UNDERLYING_OS == 'ubuntu':
        # install snap
        run_command('dpkg -i *.deb', shell=True)
    
    #elif UNDERLYING_OS == 'windows_xp':
    
    #elif UNDERLYING_OS == 'windows_7':

# disable selinux
if UNDERLYING_OS == "fedora":
    run_command(['setenforce', '0'])

if SNAP_MODE == 'test':
    # setup test prerequisites
    setup_tests()

    # checkout the source / run the test suite
    run_tests()

elif SNAP_MODE == 'build_package':
    build_package()

elif SNAP_MODE == 'install_package':
    install_snap()

elif SNAP_MODE == 'backup':
    # setup mock data
    create_mock_data()

    # run the actual backup
    run_command(['/usr/bin/snaptool', '--log-level', 'verbose', '--backup', '--snapfile', '/tmp/snapfile.tgz', '--repos', '--packages', '--files', '--services'])

elif SNAP_MODE == 'restore':
    postgres_hack()

    # run the actual restoration
    run_command(['/usr/bin/snaptool', '--log-level', 'verbose', '--restore', '--snapfile', '/tmp/snapfile.tgz'])

    # verify mock data is restored
    verify_mock_data()

