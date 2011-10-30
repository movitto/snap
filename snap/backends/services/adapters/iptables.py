#!/usr/bin/python
#
# iptables service backup/restoration adapter
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

# TODO at some point use the iptables-python api 
#  so as to not rely on calling out to the shell

import subprocess

class Iptables:

    def backup(self, basedir):
        # use a pipe to invoke iptables-save and capture output
        outfile = file(basedir + "/iptables.rules", "w")
        popen = subprocess.Popen("iptables-save", shell=True, stdout=outfile)
        popen.wait()

    def restore(self, basedir):
        # use pipe to invoke iptables-restore, restoring the rules
        infile = file(basedir + "/iptables.rules", "r")
        popen = subprocess.Popen("iptables-restore", shell=True, stdin=infile)
        popen.wait()
