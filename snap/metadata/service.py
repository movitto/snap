# Metadata pertaining to services backed up / restored by Snap!
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

import xml, xml.sax, xml.sax.handler, xml.sax.saxutils

import snap

class Service:
    """information about a service tracked by snap"""

    def __init__(self, name=''):
        '''initialize the service

        @param name - the name of the service
        '''

        self.name = name

class ServicesRecordFile:
    '''a snap service record file, contains list of services configured, to restore'''
    
    def __init__(self, filename):
        '''initialize the file

        @param filename - path to the file 
        '''

        self.servicesfile = filename

    def write(self, services):
        '''generate file containing record of services

        @param services - list of Services to record
        '''
        f=open(self.servicesfile, 'w')
        f.write("<services>")
        for service in services:
            f.write('<service>' + xml.sax.saxutils.escape(service.name) + '</service>');
        f.write("</services>")
        f.close()

    def read(self):
        '''
        read services from the file

        @returns - list of instances of Service
        '''
        parser = xml.sax.make_parser()
        parser.setFeature(xml.sax.handler.feature_namespaces, 0)
        handler = _ServicesRecordFileParser()
        parser.setContentHandler(handler)
        parser.parse(self.servicesfile)
        return handler.services
        


class _ServicesRecordFileParser(xml.sax.handler.ContentHandler):
    '''internal class to parse the services record file xml'''

    def __init__(self):
        # list of services parsed
        self.services = []

        # current service being processed
        self.current_service=None

        # flag indicating if we are evaluating a name
        self.in_service_content=False
    
    def startElement(self, name, attrs):
        if name == 'service':
            self.current_service = ''
            self.in_service_content=True

    def characters(self, ch):
        if self.in_service_content:
            self.current_service = self.current_service + ch

    def endElement(self, name):
        if name == 'service':
            self.in_service_content = False
            self.services.append(Service(name=xml.sax.saxutils.unescape(self.current_service)))
