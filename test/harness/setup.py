#!/usr/bin/python
#
# sets up a test harness for automated integration testing of snap
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
import time
import shutil
import tarfile
import tempfile
import subprocess
import xml.dom.minidom

# used to generate random uuid / mac
import virtinst.util

# some parameters to use when building the package
SNAP_VERSION='0.6'
RPM_RELEASE='8'
FEDORA_RELEASE='15'

SNAP_RPM="snap-" + SNAP_VERSION + "-" + RPM_RELEASE + ".fc" + FEDORA_RELEASE + ".noarch.rpm"
SNAP_DEB="snap_" + SNAP_VERSION + "_all.deb"

# base images which we will base instances off of
# these should have a ssh server installed on them and configured to auto-start on boot
#   (should not require any credentials for root access)
# see http://mo.morsi.org/blog/node/355 for how to do this
IMAGES = { 
   'fedora'     : '/home/libvirt/images/F15-snap.img.orig',
   'ubuntu'     : '/home/libvirt/images/ubuntu-snap.img.orig'
   #'windows_xp' : None,
   #'windows_7'  : None
}

# directories which we will store libvirt data
LIBVIRT_IMAGE_ROOT = '/home/libvirt/images'
LIBVIRT_XML_ROOT   = '/etc/libvirt/qemu'

# current working dir
CURRENT_DIR = os.path.dirname(__file__)

# helper to run a command and wait for it to complete, returns the command's stdout/stderr
def run_command(command, env=os.environ):
    t = tempfile.TemporaryFile()
    popen = subprocess.Popen(command, stdout=t, stderr=t, env=env)
    popen.wait()
    t.seek(0)
    data = t.read()
    t.close()
    return data

# helper to run a command via ssh
def ssh_command(destination, command, env=os.environ):
    return run_command(['ssh', "-o", "StrictHostKeyChecking no", "-o", "ServerAliveInterval 60", destination, command], env=env)

# helper to run a command via ssh with timeout
# XXX hack needed, see below
def ssh_command_with_timeout(destination, command, timeout="900", env=os.environ):
    return run_command(['bash', 'timeout3', '-t', timeout, 'ssh', "-o", "StrictHostKeyChecking no", "-o", "ServerAliveInterval 60", destination, command], env=env)

# helper to scp source file to dest
def scp_command(source, destination):
    return run_command(['scp', "-o", "StrictHostKeyChecking no", source, destination ])

# helper to create a libvirt instance for the specified os
def create_vm(os_name):
    print "Creating " + os_name + "-snap vm"

    source_xml_file = os.path.join(CURRENT_DIR, "libvirt.xml")
    dest_xml_file   = os.path.join(LIBVIRT_XML_ROOT, os_name + "-snap.xml")
    image_file      = os.path.join(LIBVIRT_IMAGE_ROOT, os_name + "-snap.img")
    
    # read in source xml and substitute required data
    uuid_str   = virtinst.util.uuidToString(virtinst.util.randomUUID())
    mac_str    = virtinst.util.randomMAC()
    data = open(source_xml_file, 'r').read()
    data = re.sub("NAME",     os_name + '-snap', data)
    data = re.sub("UUID",     uuid_str, data)
    data = re.sub("IMAGE",    image_file,  data)
    data = re.sub("MAC_ADDR", mac_str, data)
    
    # write dest xml
    o = open(dest_xml_file, 'w')
    o.write(data)
    o.close()
    
    # copy the libvirt image file into place
    shutil.copyfile(IMAGES[os_name], image_file)
    
    # define instance w/ libvirt and start it up
    run_command(['virsh', 'define', dest_xml_file])
    run_command(['virsh', 'start', os_name + '-snap'])
    
    # wait for a bit
    time.sleep(60)
    
    # grab and return ip address of running instance
    ip_addr = None
    output = run_command(['arp', '-n'])
    for line in output.split("\n"):
        sline = line.split()
        if sline[2] == mac_str:
            ip_addr = sline[0]
            break
    return ip_addr


# helper to update the vm
def update_vm(ip_address, os_name):
    print "Updating " + os_name + "-snap vm via " + ip_address

    # use package system to update the vm
    if os_name == 'fedora':
        ssh_command('root@' + ip_address, 'yum update -y')

    elif os_name == 'ubuntu':
        env = os.environ
        env['DEBIAN_FRONTEND']='noninteractive'
        print "updating repos"
        ssh_command('root@' + ip_address, 'apt-get update  -y', env=env)
        print "upgrading packages"
        # XXX hack needed, apt-get upgrade via ssh will not return for whatever reason,
        #   so kill it after 15 minutes
        ssh_command_with_timeout('root@' + ip_address, 'apt-get upgrade -y', "900", env=env)
        print "done"

    # restart the system
    ssh_command('root@' + ip_address, 'reboot')

    # wait for a bit
    time.sleep(60)

# helper to destroy a libvirt instance for the specified os
def destroy_vm(os_name):
    print "Destroying " + os_name + "-snap vm"

    # destroy the vm via libvirt
    run_command(['virsh', 'destroy', os_name + '-snap'])

    # wait for a bit
    time.sleep(60)

    # undefine the vm via libvirt
    run_command(['virsh', 'undefine', os_name + '-snap'])

# helper to run tests on the specified instance / os
def run_tests(ip_address, os_name):
    print "Running tests on " + os_name + "-snap vm via " + ip_address

    # copy the bootstrapping script into place
    scp_command('snap_bootstrap.py', 'root@' + ip_address + ':~/')

    # run the script
    ssh_command('root@' + ip_address, 'python snap_bootstrap.py ' + os_name + ' test')

# build package on the vm and copy it locally
def build_package(ip_address, os_name):
    print "Building package on " + os_name + "-snap vm via " + ip_address

    # copy the bootstrapping script into place
    scp_command('snap_bootstrap.py', 'root@' + ip_address + ':~/')

    # run the script
    ssh_command('root@' + ip_address, 'python snap_bootstrap.py ' + os_name + ' build_package')

    # copy the package locally
    if os_name == 'fedora':
      scp_command('root@' + ip_address + ':~/rpmbuild/RPMS/noarch/' + SNAP_RPM, '.')
    elif os_name == 'ubuntu':
      scp_command('root@' + ip_address + ':~/' + SNAP_DEB, '.')

# helper to take a snapshot on the specified instance / os
def take_snapshot(ip_address, os_name):
    print "Taking snapshot on " + os_name + "-snap vm via " + ip_address

    # copy the bootstrapping script into place
    scp_command('snap_bootstrap.py', 'root@' + ip_address + ':~/')

    # copy the snap package to the machine
    if os_name == 'fedora':
      scp_command(SNAP_RPM, 'root@' + ip_address + ':~/')
    elif os_name == 'ubuntu':
      scp_command(SNAP_DEB, 'root@' + ip_address + ':~/')

    # install snap
    ssh_command('root@' + ip_address, 'python snap_bootstrap.py ' + os_name + ' install_package')

    # run the backup operation
    ssh_command('root@' + ip_address, 'python snap_bootstrap.py ' + os_name + ' backup')

    # scp the snapshot locally
    scp_command('root@' + ip_address + ':/tmp/snapfile.tgz', '.')

# helper to verify a snapshot on the specified instance / os
def verify_snapshot(os_name):
    print "Verifying snapshot of " + os_name + "-snap vm"

    if os.path.isdir("snapdir"):
        shutil.rmtree("snapdir")
    os.mkdir('snapdir')
    os.chdir("./snapdir")
    paths = []
    tarball = tarfile.open(os.path.join("..", "snapfile.tgz"), "r")
    for tarinfo in tarball:
        paths.append(tarinfo.path)
        tarball.extract(tarinfo)
    
    assert "services.xml" in paths
    assert "packages.xml" in paths
    assert "files.xml"    in paths
    
    doc = xml.dom.minidom.parse("services.xml")
    elements = []
    for element in doc.documentElement.childNodes:
      elements.append(element.firstChild.data)
    
    assert "iptables"   in elements
    assert "postgresql" in elements
    
    doc = xml.dom.minidom.parse("packages.xml")
    elements = []
    for element in doc.documentElement.childNodes:
      elements.append(element.firstChild.data)
    
    assert "mediawiki"           in elements
    if os_name == 'fedora':
        assert "postgresql-server"   in elements
    elif os_name == 'ubuntu':
        assert "postgresql"   in elements
    
    doc = xml.dom.minidom.parse("files.xml")
    elements = []
    for element in doc.documentElement.childNodes:
      elements.append(element.firstChild.data)
    
    assert "etc/dummy.conf"   in elements
    assert "var/dummy.data"   not in elements
    
    os.chdir("..")
    shutil.rmtree("snapdir")

# helper to restore snapshot on the specified instance
def restore_snapshot(ip_address, os_name):
    print "Restoring snapshot of " + os_name + "-snap vm"

    # copy the bootstrapping script into place
    scp_command('snap_bootstrap.py', 'root@' + ip_address + ':~/')

    # copy the snap package to the machine
    if os_name == 'fedora':
      scp_command(SNAP_RPM, 'root@' + ip_address + ':~/')
    elif os_name == 'ubuntu':
      scp_command(SNAP_DEB, 'root@' + ip_address + ':~/')

    # install it
    ssh_command('root@' + ip_address, 'python snap_bootstrap.py ' + os_name + ' install_package')

    # scp the snapshot remotely
    scp_command('snapfile.tgz', 'root@' + ip_address + ':/tmp/')

    # run the script
    return ssh_command('root@' + ip_address, 'python snap_bootstrap.py ' + os_name + ' restore')

# for each image
for img_name in IMAGES.keys():
    # define / start a new vm
    ip_address = create_vm(img_name)

    # update the vm
    update_vm(ip_address, img_name)

    # run tests
    run_tests(ip_address, img_name)

    # build package / grab a copy of it locally
    build_package(ip_address, img_name)

    # take the snapshot
    take_snapshot(ip_address, img_name)

    # verify snapshots
    verify_snapshot(img_name)

    # destroy the instance
    destroy_vm(img_name)

    # startup new instances
    ip_address = create_vm(img_name)

    # restore the snapshot
    output = restore_snapshot(ip_address, img_name)

    # verify snapshot is restored on running instance
    result = re.findall("ERROR([^\n]*)\n", output)
    for res in result:
        print "Verification Error: ", res
    if len(result) != 0:
        print "Verification output: "
        print output
    assert len(result) == 0

    destroy_vm(img_name)
