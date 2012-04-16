# Metadata pertaining to repos backed up / restored by Snap!
#
# (C) Copyright 2012 Mo Morsi (mo@morsi.org)
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

class Repo:
    """information about a repository tracked by snap"""

    def __init__(self, name='', url=''):
        '''initialize the repository

        @param name - name of the repo
        @param url - url to the repo
        '''

        self.name = name
        self.url  = url

class ReposRecordFile:
    '''a snap repo record file'''
    
    def __init__(self, filename):
        '''initialize the file

        @param filename - path to the file 
        '''

        self.repofile = filename

    def write(self, repos):
        '''generate file containing record of repositories

        @param repos - list of Repos to record
        '''
        f=open(self.repofile, 'w')
        f.write("<repos>")
        for repo in repos:
            f.write('<repo>')
            f.write(xml.sax.saxutils.escape(repo.url))
            f.write('</repo>');
        f.write("</repos>")
        f.close()

    def read(self):
        '''
        read repos from the file

        @returns - list of instances of Repo
        '''
        parser = xml.sax.make_parser()
        parser.setFeature(xml.sax.handler.feature_namespaces, 0)
        handler = _ReposRecordFileParser()
        parser.setContentHandler(handler)
        parser.parse(self.repofile)
        return handler.repos
        


class _ReposRecordFileParser(xml.sax.handler.ContentHandler):
    '''internal class to parse the repos record file xml'''

    def __init__(self):
        # list of repos parsed
        self.repos = []

        # current repo being processed
        self.current_repo=None

        # flag indicating if we are evaluating a name
        self.in_repo_content=False
    
    def startElement(self, name, attrs):
        if name == 'repo':
            self.current_repo = ''
            self.in_repo_content=True

    def characters(self, ch):
        if self.in_repo_content:
            self.current_repo = self.current_repo + ch

    def endElement(self, name):
        if name == 'repo':
            self.in_repo_content = False
            self.repos.append(Repo(url=xml.sax.saxutils.unescape(self.current_repo)))
