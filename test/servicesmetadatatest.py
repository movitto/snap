#!/usr/bin/python
#
# test/servicesmetadatatest.py unit test suite for snap.metadata.services
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
import unittest

from snap.metadata.service import Service, ServicesRecordFile

class ServicesMetadataTest(unittest.TestCase):
    def testWriteServicesRecordFile(self):
        file_path = os.path.join(os.path.dirname(__file__), "data/services-out.xml")
        services  = [Service(name='foo'),
                     Service(name='baz')]

        service_record_file = ServicesRecordFile(file_path)
        service_record_file.write(services)
        f=open(file_path, 'r')
        contents = f.read()
        f.close()

        self.assertEqual("<services><service>foo</service><service>baz</service></services>", contents)
        os.remove(file_path)

    def testReadServicesRecordFile(self):
        file_path = os.path.join(os.path.dirname(__file__), "data/servicesfile.xml")
        services = ServicesRecordFile(file_path).read()
        service_names = []
        for service in services:
            service_names.append(service.name)
        self.assertIn('iptables',   service_names)
        self.assertIn('mysql',      service_names)
        self.assertIn('postgresql', service_names)
