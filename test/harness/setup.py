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

# base images which we will base instances off of
# these should have a ssh server installed on them and configured to auto-start on boot
#   (should not require any credentials for root access)
IMAGES = { 
   'fedora'     : '/home/libvirt/images/F15-snap.img.orig',
   #'ubuntu'     : '/home/libvirt/images/ubuntu-snap.img.orig'
   #'windows_xp' : None,
   #'windows_7'  : None
}

# directories which we will store libvirt data
LIBVIRT_IMAGE_ROOT = '/home/libvirt/images'
LIBVIRT_XML_ROOT   = '/etc/libvirt/qemu'

# current working dir
CURRENT_DIR = os.path.dirname(__file__)

# helper to run a command and wait for it to complete, returns the command's stdout/stderr
def run_command(command):
    t = tempfile.TemporaryFile()
    popen = subprocess.Popen(command, stdout=t, stderr=t)
    popen.wait()
    t.seek(0)
    data = t.read()
    t.close()
    return data

# helper to create a libvirt instance for the specified os
def create_vm(os_name):
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
    # use package system to update the vm
    if os_name == 'fedora':
        run_command(['ssh', "-o", "StrictHostKeyChecking no", 'root@' + ip_address, 'yum update -y'])

    elif os_name == 'ubuntu':
        run_command(['ssh', "-o", "StrictHostKeyChecking no", 'root@' + ip_address, 'apt-get update -y'])

    # restart the system
    run_command(['ssh', "-o", "StrictHostKeyChecking no", 'root@' + ip_address, 'restart'])

    # wait for a bit
    time.sleep(60)

# helper to destroy a libvirt instance for the specified os
def destroy_vm(os_name):
    # destroy the vm via libvirt
    run_command(['virsh', 'destroy', os_name + '-snap'])

    # wait for a bit
    time.sleep(60)

    # undefine the vm via libvirt
    run_command(['virsh', 'undefine', os_name + '-snap'])

# helper to run tests on the specified instance / os
def run_tests(ip_address, os_name):
    # copy the bootstrapping script into place
    run_command(['scp', "-o", "StrictHostKeyChecking no", 'snap_bootstrap.py', "root@" + ip_address + ":~/"])

    # run the script
    run_command(['ssh', "-o", "StrictHostKeyChecking no", 'root@' + ip_address, 'python snap_bootstrap.py ' + os_name + ' test'])

# helper to take a snapshot on the specified instance / os
def take_snapshot(ip_address, os_name):
    # copy the bootstrapping script into place
    run_command(['scp', "-o", "StrictHostKeyChecking no", 'snap_bootstrap.py', "root@" + ip_address + ":~/"])

    # run the script
    run_command(['ssh', "-o", "StrictHostKeyChecking no", 'root@' + ip_address, 'python snap_bootstrap.py ' + os_name + ' backup'])

    # scp the snapshot locally
    run_command(['scp', "-o", "StrictHostKeyChecking no", 'root@' + ip_address + ':/tmp/snapfile.tgz', '.'])

# helper to verify a snapshot on the specified instance / os
def verify_snapshot():
    if not os.path.isdir("snapdir"):
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
    assert "postgresql-server"   in elements
    
    doc = xml.dom.minidom.parse("files.xml")
    elements = []
    for element in doc.documentElement.childNodes:
      elements.append(element.firstChild.data)
    
    assert "/etc/dummy.conf"   in elements
    assert "/var/dummy.data"   not in elements
    
    os.chdir("..")
    shutil.rmtree("snapdir")

# helper to restore snapshot on the specified instance
def restore_snapshot(ip_address, os_name):
    # copy the bootstrapping script into place
    run_command(['scp', "-o", "StrictHostKeyChecking no", 'snap_bootstrap.py', "root@" + ip_address + ":~/"])

    # scp the snapshot remotely
    run_command(['scp', "-o", "StrictHostKeyChecking no", 'snapfile.tgz', 'root@' + ip_address + ':/tmp/'])

    # run the script
    return run_command(['ssh', "-o", "StrictHostKeyChecking no", 'root@' + ip_address, 'python snap_bootstrap.py ' + os_name + ' restore'])

# for each image
for img_name in IMAGES.keys():
    # define / start a new vm
    ip_address = create_vm(img_name)

    # update the vm
    update_vm(img_name)

    # run tests
    run_tests(ip_address, img_name)

    # destroy / recreate the instance
    destroy_vm(img_name)
    ip_address = create_vm(img_name)
    update_vm(img_name)

    # take the snapshot
    take_snapshot(ip_address, img_name)

    # verify snapshots
    verify_snapshot()

    # destroy the instance
    destroy_vm(img_name)

    # startup new instances
    ip_address = create_vm(img_name)

    # restore the snapshot
    output = restore_snapshot(ip_address, img_name)

    # verify snapshot is restored on running instance
    result = re.findall("ERROR([^\n])*\n", output)
    for res in result:
        print "Verification Error: ", res
    assert len(result) == 0
